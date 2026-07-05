"""Number setup for Enki integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator
from .const import ENKI_CAPABILITY, ENKI_CHANGE_VIBRATION_SENSIBILITY_LEVEL, ENKI_CHECK_VIBRATION_SENSIBILITY_LEVEL

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up number entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    numbers = [
        entity
        for device in coordinator.data
        for entity in _build_number_entities(coordinator, device)
    ]
    async_add_entities(numbers)


class EnkiNumber(EnkiBaseEntity, NumberEntity):
    """Representation of an Enki number."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EnkiCoordinator,
        device: dict[str, Any],
        parameter: str,
        unit: str,
        device_class: NumberDeviceClass,
        switch_capability: ENKI_CAPABILITY,
        check_capability: ENKI_CAPABILITY,
        native_min_value: float,
        native_max_value: float,
        native_step: float,
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device)
        self.parameter = parameter
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_switch_capability = switch_capability
        self._attr_check_capability = check_capability
        self.native_max_value = native_max_value
        self.native_min_value = native_min_value
        self.native_step = native_step

    @property
    def native_value(self) -> float | None:
        """Return the number value."""
        value = self.coordinator.get_device_parameter(self.node_id, self._attr_check_capability.name).get('lastReportedValue', None)
      
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
        
    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.coordinator.api.query_endpoint(self.device["homeId"], self.node_id, self._attr_switch_capability, { "value": str(int(value)) })
        self.coordinator.update_data(self.node_id,{self._attr_check_capability.name: {"lastReportedValue": str(value)}})



def _build_number_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiNumber]:
    """Create power production number for inverter devices."""
    capabilities = device.get("capabilities")
    if not isinstance(capabilities, list):
        return []


    # Check https://developers.home-assistant.io/docs/core/entity/number/ for device class, units and state class options
    supported_number_capabilities = [
        {
            'switch_capability': ENKI_CHANGE_VIBRATION_SENSIBILITY_LEVEL,
            'check_capability': ENKI_CHECK_VIBRATION_SENSIBILITY_LEVEL,
            'parameter': 'vibration_sensibility_level',
            'max_value': 5,
            'min_value': 1,
            'step': 1
        },
    ]

    numbers = []

    for cap in supported_number_capabilities:
        if cap['check_capability'].name not in capabilities:
            continue
        numbers.append(
            EnkiNumber(
                coordinator,
                device,
                parameter=cap['parameter'],
                unit=cap.get('unit', None),
                device_class=cap.get('device_class', None),
                switch_capability=cap.get('switch_capability'),
                check_capability=cap.get('check_capability'),
                native_max_value=cap.get('max_value', None),
                native_min_value=cap.get('min_value', None),
                native_step=cap.get('step', None),
            )
        )

    return numbers
