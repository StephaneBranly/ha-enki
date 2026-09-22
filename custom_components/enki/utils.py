from typing import Any

def _capabilities_set(device: dict[str, Any]) -> set[str]:
    """Return a safe capability set from device metadata."""
    capabilities = device.get("capabilities")
    if isinstance(capabilities, list):
        return {capability for capability in capabilities if isinstance(capability, str)}
    if isinstance(capabilities, dict):
        return set(capabilities.keys())
    return set()