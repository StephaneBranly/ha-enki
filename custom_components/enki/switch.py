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
from .const import ENKI_CHECK_ELECTRICAL_POWER, ENKI_SWITCH_ELECTRICAL_POWER, LOGGER

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
        device_class: SwitchDeviceClass,
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device)
        self._device = device
        self._attr_device_class = device_class

    @property
    def is_on(self) -> bool | None:
        """Return if outlet is on."""
        power = self.coordinator.get_device_capability_parameter(self.node_id, ENKI_CHECK_ELECTRICAL_POWER)
        if isinstance(power, str):
            return power == "ON"
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        LOGGER.debug('turn on')
        await self.coordinator.api.query_endpoint(self.device["homeId"], self.node_id, ENKI_SWITCH_ELECTRICAL_POWER, { "value": 'ON' })

        self.coordinator.update_data(self.node_id, {ENKI_CHECK_ELECTRICAL_POWER.name: {"lastReportedValue": 'ON'}})

    async def async_turn_off(self, **kwargs: Any) -> None:
        LOGGER.debug('turn on')
        await self.coordinator.api.query_endpoint(self.device["homeId"], self.node_id, ENKI_SWITCH_ELECTRICAL_POWER, { "value": 'OFF' })
        self.coordinator.update_data(self.node_id,{ENKI_CHECK_ELECTRICAL_POWER.name: {"lastReportedValue": 'OFF'}})

def _build_switch_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiSwitch]:
    """Create power production sensor for inverter devices."""
    capabilities = device.get("capabilities")
    if not isinstance(capabilities, list):
        return []


    # Check https://developers.home-assistant.io/docs/core/entity/sensor/ for device class, units and state class options
    supported_switch_capabilities = [
        {
            'capability': 'switch_electrical_power',
            'device_class': SwitchDeviceClass.OUTLET,
        },
    ]

    switches = []

    for cap in supported_switch_capabilities:
        if cap['capability'] not in capabilities:
            continue
        if _has_check_light_state(device):
            continue
        switches.append(
            EnkiSwitch(
                coordinator,
                device,
                device_class=cap['device_class'],
            )
        )

    LOGGER.debug(f"created {len(switches)} switch entities for device {device['nodeId']}")
    return switches
