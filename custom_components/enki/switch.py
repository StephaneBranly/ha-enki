"""Sensor setup for Enki integration."""

from __future__ import annotations

from typing import Any

from custom_components.enki.light import _has_check_light_state
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator
from .const import ENKI_ACTIVATE_CONTACT_DETECTION, ENKI_ACTIVATE_VIBRATION_DETECTION, ENKI_CAPABILITY, ENKI_CHECK_CONTACT_DETECTION_ACTIVATION, ENKI_CHECK_ELECTRICAL_POWER, ENKI_CHECK_SIREN_GLOBAL_STATUS, ENKI_CHECK_VIBRATION_DETECTION_ACTIVATION, ENKI_SWITCH_ELECTRICAL_POWER, ENKI_SWITCH_SIREN_STATUS

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up switch entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    switch = [
        entity
        for device in coordinator.data
        for entity in _build_switch_entities(coordinator, device)
    ]
    async_add_entities(switch)


class EnkiSwitch(EnkiBaseEntity, SwitchEntity):
    """Representation of an Enki sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EnkiCoordinator,
        device: dict[str, Any],
        parameter: str,
        device_class: SwitchDeviceClass,
        switch_capability: ENKI_CAPABILITY,
        check_capability: ENKI_CAPABILITY
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device)
        self.parameter = parameter
        self._device = device
        self._attr_device_class = device_class
        self._attr_switch_capability = switch_capability
        self._attr_check_capability = check_capability

    @property
    def is_on(self) -> bool | None:
        """Return if outlet is on."""
        power = self.coordinator.get_device_capability_parameter(self.node_id, self._attr_check_capability)
        if isinstance(power, str):
            return power == "ON"
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.query_endpoint(self.device["homeId"], self.node_id, self._attr_switch_capability, { "value": 'ON' })
        self.coordinator.update_data(self.node_id, {self._attr_check_capability.name: {"lastReportedValue": 'ON'}})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.query_endpoint(self.device["homeId"], self.node_id, self._attr_switch_capability, { "value": 'OFF' })
        self.coordinator.update_data(self.node_id,{self._attr_check_capability.name: {"lastReportedValue": 'OFF'}})

def _build_switch_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiSwitch]:
    """Create power production sensor for inverter devices."""
    capabilities = device.get("capabilities")
    if not isinstance(capabilities, list):
        return []

    # Check https://developers.home-assistant.io/docs/core/entity/sensor/ for device class, units and state class options
    supported_switch_capabilities = [
        {
            'switch_capability': ENKI_SWITCH_ELECTRICAL_POWER,
            'check_capability': ENKI_CHECK_ELECTRICAL_POWER,
            'device_class': SwitchDeviceClass.OUTLET,
            'parameter': 'electrical_power'
        },
        {
            'switch_capability': ENKI_ACTIVATE_VIBRATION_DETECTION,
            'check_capability': ENKI_CHECK_VIBRATION_DETECTION_ACTIVATION,
            'device_class': SwitchDeviceClass.SWITCH,
            'parameter': 'vibration_detection'
        },
        {
            'switch_capability': ENKI_ACTIVATE_CONTACT_DETECTION,
            'check_capability': ENKI_CHECK_CONTACT_DETECTION_ACTIVATION,
            'device_class': SwitchDeviceClass.SWITCH,
            'parameter': 'contact_detection'
        },
        {
            # TO DO : use Siren Entity type for siren
            'switch_capability': ENKI_SWITCH_SIREN_STATUS,
            'check_capability': ENKI_CHECK_SIREN_GLOBAL_STATUS,
            'device_class': SwitchDeviceClass.SWITCH,
            'parameter': 'siren'
        },
    ]

    switches = []

    for cap in supported_switch_capabilities:
        if cap['switch_capability'].name not in capabilities:
            continue

        if _has_check_light_state(device):
            continue
        switches.append(
            EnkiSwitch(
                coordinator,
                device,
                cap.get('parameter', None),
                device_class=cap['device_class'],
                switch_capability=cap.get('switch_capability'),
                check_capability=cap.get('check_capability'),
            )
        )

    return switches
