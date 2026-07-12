"""BinarySensor setup for Enki integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator
from .const import ENKI_CHECK_CONTACT_SENSOR_STATE, ENKI_CHECK_MOTION_DETECTION, ENKI_CHECK_VIBRATION_DETECTION, ENKI_CHECK_WATER_SENSOR_STATE

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up binary_sensor entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    binary_sensors = [
        entity
        for device in coordinator.data
        for entity in _build_binary_sensor_entities(coordinator, device)
    ]
    async_add_entities(binary_sensors)


class EnkiBinarySensor(EnkiBaseEntity, BinarySensorEntity):
    """Representation of an Enki binary_sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EnkiCoordinator,
        device: dict[str, Any],
        parameter: str,
        key: str,
        device_class: BinarySensorDeviceClass,
        conversion_table: dict | None = None
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device)
        self.parameter = parameter
        self._key = key
        self._attr_device_class = device_class
        self._attr_conversion_table = conversion_table

    @property
    def is_on(self) -> float | None:
        """Return the binary_sensor value."""
        getv = self.coordinator.get_device_parameter(self.node_id, self._key)
        value = getv.get('lastReportedValue', None)
        if self._attr_conversion_table:
            value = self._attr_conversion_table.get(value, None)
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def _build_binary_sensor_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiBinarySensor]:
    """Create power production binary_sensor for inverter devices."""
    capabilities = device.get("capabilities")
    if not isinstance(capabilities, list):
        return []


    # Check https://developers.home-assistant.io/docs/core/entity/binary-sensor/ for device class, units and state class options
    supported_binary_sensor_capabilities = [
        {
            'capability': ENKI_CHECK_MOTION_DETECTION,
            'parameter': 'motion_detection',
            'device_class': BinarySensorDeviceClass.MOTION,
            'conversion_table': { 'MOTION_DETECTED': True, 'NO_MOTION_DETECTED': False }
        },
        {
            'capability': ENKI_CHECK_VIBRATION_DETECTION,
            'parameter': 'vibration_detection',
            'device_class': BinarySensorDeviceClass.VIBRATION,
            'conversion_table': { 'VIBRATION_DETECTED': True, 'NO_VIBRATION_DETECTED': False }
        },
        {
            'capability': ENKI_CHECK_CONTACT_SENSOR_STATE,
            'parameter': 'contact_sensor',
            'device_class': BinarySensorDeviceClass.OPENING,
            'conversion_table': { 'OPENED': True, 'CLOSED': False }
        },
        {
            'capability': ENKI_CHECK_WATER_SENSOR_STATE,
            'parameter': 'water_leak',
            'device_class': BinarySensorDeviceClass.MOISTURE,
            'conversion_table': { 'WATER_DETECTED': True, 'NO_WATER_DETECTED': False }
        }
    ]

    binary_sensors = []

    for cap in supported_binary_sensor_capabilities:
        if cap['capability'].name not in capabilities:
            continue
        binary_sensors.append(
            EnkiBinarySensor(
                coordinator,
                device,
                parameter=cap['parameter'],
                key=cap['capability'].name,
                device_class=cap['device_class'],
                conversion_table=cap.get('conversion_table', None)
            )
        )

    return binary_sensors
