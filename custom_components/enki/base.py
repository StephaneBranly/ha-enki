"""Base entity which all other entity platform classes can inherit.

As all entity types have a common set of properties, you can
create a base entity like this and inherit it in all your entity platforms.

This just makes your code more efficient and is totally optional.

See each entity platform (ie sensor.py, switch.py) for how this is inheritted
and what additional properties and methods you need to add for each entity type.

"""

import logging
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EnkiCoordinator

_LOGGER = logging.getLogger(__name__)


class EnkiBaseEntity(CoordinatorEntity):
    """Base Entity Class.

    This inherits a CoordinatorEntity class to register your entites to be updated
    by your DataUpdateCoordinator when async_update_data is called, either on the scheduled
    interval or by forcing an update.
    """

    coordinator: EnkiCoordinator

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: EnkiCoordinator, device: dict[str, Any]
    ) -> None:
        """Initialise entity."""
        super().__init__(coordinator)
        self.device = device
        self.node_id = device["nodeId"]
        self.device_id = device["deviceId"]
        self.parameter = self.coordinator.get_device_parameter(self.node_id, "deviceName")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.device["isEnabled"] & (self.device["state"] != "DEACTIVATED")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_node(self.node_id)
        _LOGGER.debug(
            "Updating device: %s, %s",
            self.node_id,
            self.coordinator.get_device_parameter(self.node_id, "deviceName"),
        )
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_name = self.coordinator.get_device_parameter(self.node_id, "deviceName")
        return DeviceInfo(
            name=device_name,
            manufacturer=self.coordinator.get_device_parameter(self.node_id, "manufacturerId"),
            model=str(
                self.coordinator.get_device_parameter(self.node_id, "modelNumber")
            )
            .replace("_", " ")
            .title(),
            model_id=str(self.coordinator.get_device_parameter(self.node_id, "deviceId")),
            sw_version=self.coordinator.get_device_parameter(
                self.node_id, "version"
            ),
            identifiers={
                (
                    DOMAIN,
                    self.node_id,
                )
            },
            serial_number=self.coordinator.get_device_parameter(self.node_id, "eui64")
        )

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self.parameter.replace("_", " ").title()

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return f"{DOMAIN}-{self.coordinator.get_device_parameter(self.node_id, "nodeId")}-{self.parameter}"
