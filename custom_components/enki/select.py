"""Select setup for Enki integration (roller shutter wiring mode)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.enki.const import (
    ENKI_CHANGE_ROLLER_SHUTTER_MODE,
    ENKI_CHECK_ROLLER_SHUTTER_STATE,
)

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up select entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    selects = [
        EnkiRollerShutterModeSelect(coordinator, device)
        for device in coordinator.data
        if _supports_shutter_mode(device)
    ]

    async_add_entities(selects)


class EnkiRollerShutterModeSelect(EnkiBaseEntity, SelectEntity):
    """Wiring/direction mode of a roller shutter (NORMAL / INVERTED).

    This is an installation-time configuration: INVERTED compensates for reversed
    motor wiring so that "open" actually opens. It is rarely changed after setup.
    """

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: EnkiCoordinator, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device)
        self.parameter = "roller_shutter_mode"
        self._attr_options = _shutter_mode_options(device)

    @property
    def current_option(self) -> str | None:
        """Return current wiring mode."""
        mode = self.coordinator.get_device_capability_parameter(
            self.node_id, ENKI_CHECK_ROLLER_SHUTTER_STATE, "shutterModeEnum"
        )
        if isinstance(mode, str) and mode in self._attr_options:
            return mode
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the wiring mode."""
        if option not in self._attr_options:
            raise ValueError(f"Unsupported mode: {option}")
        await self.coordinator.api.query_endpoint(
            self.device["homeId"],
            self.node_id,
            ENKI_CHANGE_ROLLER_SHUTTER_MODE,
            {"value": option},
        )
        self.coordinator.update_data(
            self.node_id,
            {ENKI_CHECK_ROLLER_SHUTTER_STATE.name: {"lastReportedValue": {"shutterModeEnum": option}}},
        )


def _possible_values_dict(device: dict[str, Any]) -> dict[str, Any]:
    possible_values = device.get("possibleValues")
    if isinstance(possible_values, dict):
        return possible_values
    return {}


def _shutter_mode_options(device: dict[str, Any]) -> list[str]:
    """Read mode options from possibleValues, defaulting to NORMAL/INVERTED."""
    meta = _possible_values_dict(device).get("change_roller_shutter_mode")
    if isinstance(meta, dict):
        values = meta.get("values")
        if isinstance(values, list):
            options = [value for value in values if isinstance(value, str)]
            if options:
                return options
    return ["NORMAL", "INVERTED"]


def _supports_shutter_mode(device: dict[str, Any]) -> bool:
    """Detect roller shutter devices exposing the mode capability."""
    capabilities = device.get("capabilities")
    if isinstance(capabilities, list):
        return "change_roller_shutter_mode" in capabilities
    if isinstance(capabilities, dict):
        return "change_roller_shutter_mode" in capabilities
    return False
