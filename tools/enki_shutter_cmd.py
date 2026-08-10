"""Send ONE roller shutter command to Enki (WRITE / POST).

WARNING: with --confirm this physically moves a shutter. Without --confirm it
is a dry-run: it reads and prints the current state but sends no command.

Uses the same API family validated read-only earlier:
  POST /api-enki-rolling-prod/v1/shutter/<node_id>/change-shutter-position {"value": N}
  POST /api-enki-rolling-prod/v1/shutter/<node_id>/stop-change-shutter-position  (no body)

Usage (dry-run):
  python tools/enki_shutter_cmd.py --user <email> --password <pwd> --position 50
Usage (really move):
  python tools/enki_shutter_cmd.py --user <email> --password <pwd> --position 50 --confirm
  python tools/enki_shutter_cmd.py --user <email> --password <pwd> --stop --confirm

Credentials via --user/--password or ENKI_USER/ENKI_PASSWORD. Never hard-coded.
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

sys.path.insert(1, os.path.join(sys.path[0], "../custom_components/enki"))


def _load_enki():
    component_dir = Path(__file__).resolve().parents[1] / "custom_components" / "enki"
    pkg = "_enki_cmd_runtime"
    if pkg not in sys.modules:
        m = types.ModuleType(pkg)
        m.__path__ = [str(component_dir)]
        sys.modules[pkg] = m

    def _load(name: str, filename: str):
        full = f"{pkg}.{name}"
        if full in sys.modules:
            return sys.modules[full]
        spec = importlib.util.spec_from_file_location(full, component_dir / filename)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)
        return mod

    const = _load("const", "const.py")
    api = _load("api", "api.py")
    return const, api.API


async def _find_home_for_node(api, node_id: str) -> str | None:
    homes = await api.get_homes()
    for home_id in homes:
        try:
            node = await api.get_node(home_id, node_id)
        except Exception:
            node = None
        if isinstance(node, dict) and node.get("id"):
            return home_id
    return homes[0] if homes else None


async def _read_state(api, const, home_id: str, node_id: str) -> Any:
    state = await api.query_endpoint(home_id, node_id, const.ENKI_CHECK_ROLLER_SHUTTER_STATE)
    print(f"  current state: {json.dumps(state, ensure_ascii=False)}")
    return state


async def _run(user, password, node_id, home_id, position, do_stop, confirm) -> None:
    const, API = _load_enki()
    api = API(user, password)
    if await api.connect() is not True:
        raise RuntimeError("login failed")

    if home_id is None:
        home_id = await _find_home_for_node(api, node_id)
    label = await api.get_node(home_id, node_id)
    name = label.get("label") if isinstance(label, dict) else node_id
    print(f"Target shutter: {name} (node {node_id}, home {home_id})")

    print("Reading current state (GET, read-only)...")
    await _read_state(api, const, home_id, node_id)

    if do_stop:
        action, cap, data = "STOP movement", const.ENKI_STOP_CHANGE_SHUTTER_POSITION, None
    else:
        action, cap, data = f"SET position -> {position}", const.ENKI_CHANGE_SHUTTER_POSITION, {"value": position}

    if not confirm:
        print(f"\n[DRY-RUN] Would POST: {action}")
        print(f"          endpoint: {api.get_full_endpoint(cap, home_id, node_id)}")
        print(f"          body: {json.dumps(data)}")
        print("Re-run with --confirm to actually move the shutter.")
        return

    print(f"\n[CONFIRMED] Sending POST: {action} ...")
    await api.query_endpoint(home_id, node_id, cap, data)
    print("  command sent.")

    # give the device a moment, then read back
    await asyncio.sleep(3)
    print("Reading state back...")
    await _read_state(api, const, home_id, node_id)


def main() -> int:
    p = argparse.ArgumentParser(description="Send one Enki roller shutter command (WRITE).")
    p.add_argument("--user", default=os.getenv("ENKI_USER"))
    p.add_argument("--password", default=os.getenv("ENKI_PASSWORD"))
    p.add_argument("--node-id", required=True, help="Target roller shutter node id")
    p.add_argument("--home-id", default=None)
    p.add_argument("--position", type=int, default=None, help="Target 0-100 (0=closed, 100=open)")
    p.add_argument("--stop", action="store_true", help="Stop movement instead of setting a position")
    p.add_argument("--confirm", action="store_true", help="Actually send the POST (else dry-run)")
    args = p.parse_args()

    if not args.user or not args.password:
        print("Missing credentials. Use --user/--password or ENKI_USER/ENKI_PASSWORD.")
        return 2
    if not args.stop and args.position is None:
        print("Provide --position 0-100 or --stop.")
        return 2
    if args.position is not None and not (0 <= args.position <= 100):
        print("--position must be 0-100.")
        return 2

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            _run(args.user, args.password, args.node_id, args.home_id,
                 args.position, args.stop, args.confirm)
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
