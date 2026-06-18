"""Standalone live diagnostics for Enki API (no pytest required)."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
import types
from prettytable import PrettyTable


from pathlib import Path
from typing import Any

sys.path.insert(1, os.path.join(sys.path[0], '../custom_components/enki'))
sys.path.insert(1, os.path.join(sys.path[0], '../tools'))

from const import ENKI_CAPABILITY
from update_documentation import compute_coverage


def _load_enki_api_class():
    """Load API class without importing Home Assistant integration package."""
    component_dir = Path(__file__).resolve().parents[1] / "custom_components" / "enki"
    
    package_name = "_enki_tools_runtime"

    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(component_dir)]
        sys.modules[package_name] = package

    const_module_name = f"{package_name}.const"
    if const_module_name not in sys.modules:
        const_spec = importlib.util.spec_from_file_location(
            const_module_name,
            component_dir / "const.py",
        )
        if const_spec is None or const_spec.loader is None:
            raise RuntimeError("Could not load const.py for live API script")
        const_module = importlib.util.module_from_spec(const_spec)
        sys.modules[const_module_name] = const_module
        const_spec.loader.exec_module(const_module)

    api_module_name = f"{package_name}.api"
    api_spec = importlib.util.spec_from_file_location(
        api_module_name,
        component_dir / "api.py",
    )
    if api_spec is None or api_spec.loader is None:
        raise RuntimeError("Could not load api.py for live API script")

    api_module = importlib.util.module_from_spec(api_spec)
    sys.modules[api_module_name] = api_module
    api_spec.loader.exec_module(api_module)

    return api_module.API


async def _run_live_api_check(user: str, password: str) -> None:
    api_cls = _load_enki_api_class()

    api = api_cls(user, password)

    connected = await api.connect()
    if connected is not True:
        raise RuntimeError("Enki API login did not return True")
    print('Fetching all devices...')
    devices = await api.get_devices()
    if not isinstance(devices, list):
        raise RuntimeError("Enki API did not return a device list")
    capabilities = ENKI_CAPABILITY.__subclasses__()
    print(f"\nDevices found: {len(devices)}")
    table = PrettyTable()
    table.field_names = ["#", "Name", "Device type", "Device ID", "Node ID", "Status", "Expected coverage (%)", "Protocols"]
    new_devices = []
    for index, device in enumerate(devices, start=1):
        name = device.get("deviceName") or "unknown-device"
        device_kind = device.get("deviceType") or "unknown-deviceType"
        node_id = device.get("nodeId") or "unknown-node"
        device_id = device.get("deviceId") or "unknown-node"
        protocols = device.get('protocols') or []

        device_description = {
            "manufacturer": device.get('manufacturerId', None),
            "capabilities":device.get('capabilities', []),
            "deviceId": device.get('deviceId', None),
            "possibleValues": device.get('possibleValues', None),
            "hasProgrammer": device.get('hasProgrammer', None),
            "hasTimer": device.get('hasTimer', None),
            "protocols":  device.get('protocols', None),
            "tested": False,
            "image": "photo.png",
            "name": "DEVICE_NAME"
        }
        coverage = compute_coverage(device_description, capabilities)
        device_file = Path("./doc/devices") / f"{device.get('deviceId', None)}.json"
        status = 'Known'
        if not device_file.exists():
            device_file.parent.mkdir(parents=True, exist_ok=True)
            with device_file.open(mode='w', encoding='utf-8') as f:
                f.write(json.dumps(device_description, indent=2))
            new_devices.append({**device, "index": index, "name": name})
        if len([nd for nd in new_devices if nd.get('deviceId') == device.get('deviceId', None)]):
            status = 'NEW!'
        
        table.add_row([index, name, device_kind, device_id, node_id, status, coverage, ', '.join(protocols)])
       
    print(table)

    if len(new_devices):
        print("\nYou have devices that haven't been listed or tested in this library yet.")
        print("Please submit a documentation PR to add them; you can add their names and include an image by editing the corresponding JSON files in the folder doc/devices")
        print()
        [print(f" - #{new_device.get('index')} > {new_device.get('deviceId', None)} ({new_device.get('name')})") for new_device in new_devices]

def _run_async(coro: Any) -> None:
    """Run async code with a Windows-compatible event loop policy."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
        # Let pending transport callbacks flush before closing the loop.
        loop.run_until_complete(asyncio.sleep(0))
    finally:
        asyncio.set_event_loop(None)
        loop.close()


def main() -> int:
    """Entry point for standalone live diagnostics script."""
    parser = argparse.ArgumentParser(
        description="Run Enki live API diagnostics (equivalent to tests/test_api_live.py, without pytest)."
    )
    parser.add_argument("--user", default=os.getenv("ENKI_USER"), help="Enki username/email")
    parser.add_argument("--password", default=os.getenv("ENKI_PASSWORD"), help="Enki password")
    args = parser.parse_args()

    if not args.user or not args.password:
        print("Missing credentials. Set ENKI_USER and ENKI_PASSWORD or pass --user/--password.")
        return 2

    try:
        _run_async(_run_live_api_check(args.user, args.password))
    except Exception as exc:  # pragma: no cover - defensive path for runtime diagnostics script
        print(f"Error running live diagnostics: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
