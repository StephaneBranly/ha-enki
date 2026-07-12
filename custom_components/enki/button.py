"""Sensor setup for Enki integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.button import (
    ButtonEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.enki.const import ENKI_SCENARIO_ACTIVATE_CAPABILITY, LOGGER

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up button entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    button = [
        entity
        for device in coordinator.data
        for entity in _build_button_entities(coordinator, device)
    ]
    async_add_entities(button)


class EnkiButton(EnkiBaseEntity, ButtonEntity):
    """Representation of an Enki sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EnkiCoordinator,
        device: dict[str, Any],
        name: str,
        scenario_id: str = None,
        isEnabled: bool = True,
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device)
        self.parameter = name
        self._scenario_id = scenario_id
        self._device = device
        self._attr_name = name
        self._isEnabled = isEnabled
    
    @property
    def available(self):
        return super().available and self._isEnabled

    async def async_press(self) -> None:
        await self.coordinator.api.query_endpoint(self._device["homeId"], self._scenario_id, ENKI_SCENARIO_ACTIVATE_CAPABILITY)

def _build_button_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiButton]:
    """Create power production sensor for inverter devices."""
    type = device.get("type")
    if type != 'scenarios':
        return []

    buttons = []
    LOGGER.debug("Building button entities for device: %s", device)
    for cap in device.get('scenarios', []):
        buttons.append(
            EnkiButton(
                coordinator,
                device,
                name=cap.get('scenarioName', 'Unknown'),
                scenario_id=cap.get('scenarioId', None),
                isEnabled=cap.get('isEnabled', True)
            )
        )

    return buttons

