"""Sensor setup for Enki integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator
from .const import ENKI_CHECK_BATTERY_HEALTH, ENKI_CHECK_CURRENT_HUMIDITY, ENKI_CHECK_CURRENT_TEMPERATURE, LOGGER

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up sensor entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    sensors = [
        entity
        for device in coordinator.data
        for entity in _build_sensor_entities(coordinator, device)
    ]
    async_add_entities(sensors)


class EnkiSensor(EnkiBaseEntity, SensorEntity):
    """Representation of an Enki sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EnkiCoordinator,
        device: dict[str, Any],
        parameter: str,
        key: str,
        unit: str,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass,
        conversion_table: dict | None
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator, device)
        self.parameter = parameter
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_conversion_table = conversion_table

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        value = self.coordinator.get_device_parameter(self.node_id, self._key).get('lastReportedValue', None)
        if self._attr_conversion_table:
            value = self._attr_conversion_table.get(value, None)
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def _build_sensor_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiSensor]:
    """Create power production sensor for inverter devices."""
    capabilities = device.get("capabilities")
    if not isinstance(capabilities, list):
        return []


    # Check https://developers.home-assistant.io/docs/core/entity/sensor/ for device class, units and state class options
    supported_sensor_capabilities = [
        {
            'capability': ENKI_CHECK_CURRENT_HUMIDITY,
            'parameter': 'humidity',
            'unit': "%",
            'device_class': SensorDeviceClass.HUMIDITY,
            'state_class': SensorStateClass.MEASUREMENT,
        },
        {
            'capability': ENKI_CHECK_CURRENT_TEMPERATURE,
            'parameter': 'temperature',
            'unit': "°C",
            'device_class': SensorDeviceClass.TEMPERATURE,
            'state_class': SensorStateClass.MEASUREMENT,
        },
       
        # {
        #     'capability': 'check_electrical_consumption',
        #     'parameter': 'electrical_consumption',
        #     'key': 'descriptionValue',
        #     'unit': "Wh",
        #     'device_class': SensorDeviceClass.ENERGY,
        #     'state_class': SensorStateClass.TOTAL,
        # },
        {
            'capability': ENKI_CHECK_BATTERY_HEALTH,
            'parameter': 'battery_health',
            'conversion_table':{
                    "GOOD": 80,
                    "LOW": 30,
                    "LOW_INTERNAL_BATTERY_OF_DEVICE": 30,
                    "REPLACE": 1,
                    "UNKNOWN": None,
                    "CRITICAL": 5
                },
            'unit': "%",
            'device_class': SensorDeviceClass.BATTERY,
            'state_class': SensorStateClass.MEASUREMENT,
        }
    ]

    sensors = []

    for cap in supported_sensor_capabilities:
        if cap['capability'].name not in capabilities:
            continue
        sensors.append(
            EnkiSensor(
                coordinator,
                device,
                parameter=cap['parameter'],
                key=cap['capability'].name,
                unit=cap['unit'],
                device_class=cap['device_class'],
                state_class=cap['state_class'],
                conversion_table=cap.get('conversion_table', None)
            )
        )

    LOGGER.debug(f"created {len(sensors)} sensor entities for device {device['nodeId']}")
    return sensors
