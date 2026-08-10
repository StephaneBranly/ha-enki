"""Read-only GET probe for Enki roller shutter (cover) support discovery.

SAFE: performs GET requests only. Never sends POST / change / stop / execute
commands, so it can never move a shutter.

Goal: discover the roller-shutter API family (base path + X-Gateway-APIKey) and
the JSON shape of its check_* endpoints, so `cover.py` can be implemented.

Discovery vectors (in order of reliability):
  1. Raw BFF dashboard JSON  -> item.metadata.mainChangeCapability.endpoints
     usually reveals the real capability endpoint path (and sometimes the key).
  2. Raw node JSON + raw device (referential) JSON for the target shutter.
  3. Best-effort GET probe of candidate check_* URLs: the HTTP status code
     alone tells path validity (404 = wrong path, 401/403 = path plausible but
     wrong/missing key, 200 = hit).

Usage:
  python tools/enki_shutter_probe.py --user <email> --password <pwd>
  # optional: --node-id <id> --device-id <id> --home-id <id>

Credentials are read from --user/--password or ENKI_USER/ENKI_PASSWORD env vars.
Never hard-code them.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
import types
from pathlib import Path
from typing import Any

import aiohttp

sys.path.insert(1, os.path.join(sys.path[0], "../custom_components/enki"))

# check_* capabilities to probe (GET only). Names as in the device dump; the API
# path uses hyphenated form (see API.get_api_name).
CHECK_CAPABILITIES = [
    "check_roller_shutter_state",
    "check_shutter_position",
]

# Confirmed roller-shutter family (reverse-engineered from Enki APK 2.25.1,
# cross-checked against cyrilcolinet/enki-integration-hass):
#   path   : /api-enki-rolling-prod/v1/shutter/<node_id>/<capability>
#   apikey : ENKI_ACCESS_MOTORIZATION_API_KEY
# GET on the check_* capabilities is read-only and must return 200 with the
# current shutter state/position. Older leftover candidates kept for reference.
SHUTTER_API_KEY = "QegWuQR3zSKLlJZ2OITv94vjtSaaPkDp"
NODE_KEY_PLACEHOLDER = None  # filled at runtime with the node key

# (base_path_template, api_key) pairs. api_key None => use the node key placeholder.
CANDIDATE_PATHS = [
    ("/api-enki-rolling-prod/v1/shutter/<node_id>/<capability>", SHUTTER_API_KEY),
    ("/api-enki-access-and-motorizations-prod/v1/shutter/<node_id>/<capability>", SHUTTER_API_KEY),
    ("/api-enki-roller-shutter-prod/v1/roller-shutters/<node_id>/<capability>", None),
]


def _load_enki():
    """Load const + API from the integration without importing Home Assistant."""
    component_dir = Path(__file__).resolve().parents[1] / "custom_components" / "enki"
    pkg = "_enki_probe_runtime"
    if pkg not in sys.modules:
        m = types.ModuleType(pkg)
        m.__path__ = [str(component_dir)]
        sys.modules[pkg] = m

    def _load(name: str, filename: str):
        full = f"{pkg}.{name}"
        if full in sys.modules:
            return sys.modules[full]
        spec = importlib.util.spec_from_file_location(full, component_dir / filename)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load {filename}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)
        return mod

    const = _load("const", "const.py")
    api = _load("api", "api.py")
    return const, api.API


async def _raw_get(api, url: str, api_key: str, home_id: str | None) -> tuple[int, Any]:
    """Perform a single GET and return (status, body). GET only, never mutates."""
    await api.check_connected()
    headers = {
        "Authorization": f"{api._token_type} {api._access_token}",
        "X-Gateway-APIKey": api_key,
    }
    if home_id:
        headers["homeId"] = home_id
    async with aiohttp.ClientSession() as session, session.request(
        method="GET", url=url, headers=headers
    ) as resp:
        try:
            body: Any = await resp.json()
        except Exception:
            body = await resp.text()
        return resp.status, body


def _dump(out_dir: Path, name: str, data: Any) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {path}")


async def _find_home_for_node(api, const, node_id: str) -> str | None:
    """Return the home_id whose node list contains node_id, else None."""
    homes = await api.get_homes()
    for home_id in homes:
        try:
            node = await api.get_node(home_id, node_id)
        except Exception:
            node = None
        if isinstance(node, dict) and node.get("id"):
            return home_id
    return homes[0] if homes else None


async def _run(user: str, password: str, node_id: str, device_id: str | None,
               home_id: str | None) -> None:
    const, API = _load_enki()
    api = API(user, password)
    if await api.connect() is not True:
        raise RuntimeError("login failed")

    out_dir = Path("./doc/devices/probe")
    print("Connected. Dumping raw JSON...")

    # --- homes ---
    homes = await api.get_homes()
    _dump(out_dir, "homes", homes)
    if home_id is None:
        home_id = await _find_home_for_node(api, const, node_id)

    # Derive the referential device id from the node when not supplied.
    if device_id is None:
        node = await api.get_node(home_id, node_id)
        if isinstance(node, dict):
            device_id = node.get("deviceId")
    print(f"Using home_id={home_id} node_id={node_id} device_id={device_id}")

    # --- 1. raw BFF dashboard (best discovery vector) ---
    try:
        bff = await api.query_endpoint(home_id, None, const.ENKI_BFF_ITEMS)
        _dump(out_dir, "bff_dashboard", bff)
        _scan_bff_for_shutter(bff, node_id, device_id)
    except Exception as exc:
        print(f"  BFF dump failed: {exc!r}")

    # --- 2. raw node + referential device ---
    try:
        node = await api.get_node(home_id, node_id)
        _dump(out_dir, f"node_{node_id}", node)
    except Exception as exc:
        print(f"  node dump failed: {exc!r}")
    if device_id:
        try:
            device = await api.get_device(device_id)
            _dump(out_dir, f"device_{device_id}", device)
        except Exception as exc:
            print(f"  device dump failed: {exc!r}")

    # --- 3. best-effort GET probe of candidate check_* endpoints ---
    print("\nProbing candidate roller-shutter check_* endpoints (GET only)...")
    node_key = const.ENKI_NODE_ENDPOINT.x_api_key  # placeholder key for unknown families
    results: list[dict[str, Any]] = []
    for tmpl, cand_key in CANDIDATE_PATHS:
        probe_key = cand_key or node_key
        for cap in CHECK_CAPABILITIES:
            api_cap = cap.replace("_", "-")
            path = tmpl.replace("<node_id>", node_id).replace("<capability>", api_cap)
            url = f"{const.ENKI_URL}{path}"
            try:
                status, body = await _raw_get(api, url, probe_key, home_id)
            except Exception as exc:
                status, body = -1, repr(exc)
            hit = status == 200
            marker = "  <== HIT" if hit else ""
            print(f"  [{status}] {path}{marker}")
            results.append({"path": path, "capability": cap, "status": status,
                            "body": body if (hit or status in (401, 403)) else None})
    _dump(out_dir, "probe_results", results)

    print("\nDone. Inspect doc/devices/probe/*.json")
    print("Key files: bff_dashboard.json (look for mainChangeCapability.endpoints),")
    print("           probe_results.json (status 200=hit, 401/403=path plausible, 404=wrong).")


def _scan_bff_for_shutter(bff: Any, node_id: str, device_id: str) -> None:
    """Print any capability/endpoint metadata tied to the target shutter."""
    if not isinstance(bff, dict):
        return
    for section in bff.get("sections", []):
        for item in section.get("items", []):
            meta = item.get("metadata", {})
            if meta.get("nodeId") == node_id or meta.get("deviceId") == device_id:
                print("\n  BFF item matched target shutter:")
                for key in ("deviceType", "mainChangeCapabilityId",
                            "mainCheckCapabilityId", "mainChangeCapability",
                            "mainCheckCapability"):
                    if key in meta:
                        print(f"    {key}: {json.dumps(meta[key], ensure_ascii=False)}")


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only GET probe for Enki roller shutters.")
    p.add_argument("--user", default=os.getenv("ENKI_USER"))
    p.add_argument("--password", default=os.getenv("ENKI_PASSWORD"))
    p.add_argument("--node-id", required=True, help="Roller shutter node id to probe")
    p.add_argument("--device-id", default=None, help="Referential device id (derived from node if omitted)")
    p.add_argument("--home-id", default=None)
    args = p.parse_args()

    if not args.user or not args.password:
        print("Missing credentials. Use --user/--password or ENKI_USER/ENKI_PASSWORD.")
        return 2

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            _run(args.user, args.password, args.node_id, args.device_id, args.home_id)
        )
        loop.run_until_complete(asyncio.sleep(0))
    except Exception as exc:
        print(f"Error: {exc!r}")
        return 1
    finally:
        asyncio.set_event_loop(None)
        loop.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
