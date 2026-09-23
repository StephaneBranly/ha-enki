"""Integration 101 Template integration using DataUpdateCoordinator."""
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import DOMAIN, HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API, APIAuthError
from .const import DEFAULT_SCAN_INTERVAL, ENKI_CAPABILITY, ENKI_CHECK_ELECTRICAL_POWER, LOGGER

class EnkiCoordinator(DataUpdateCoordinator):
    """My Enki coordinator."""

    data: list[dict[str, Any]]

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]

        # read polling interval from config entry data, falling back to default
        self.poll_interval = int(config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        self._device_update_intervals: dict[str, int] = {}
        self._device_refresh_unsub: dict[str, Callable[[], None]] = {}

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here
        self.api = API(user=self.user, pwd=self.pwd)

    def get_device_update_interval(self, node_id: str) -> int:
        """Return the refresh interval configured for a given device."""
        if device := self.get_node(node_id):
            return int(device.get("update_interval", self.poll_interval))
        return self.poll_interval

    def set_device_update_interval(self, node_id: str, seconds: float) -> None:
        """Update the refresh interval for a specific device and reschedule it."""
        interval = max(1, int(seconds))
        device = self.get_node(node_id)
        if isinstance(device, dict):
            device["update_interval"] = interval
        self._device_update_intervals[node_id] = interval
        self._reschedule_device_update(node_id, interval)

    @callback
    def _reschedule_device_update(self, node_id: str, interval: int) -> None:
        """Restart the scheduled refresh for a device with a new cadence."""
        if node_id in self._device_refresh_unsub:
            self._device_refresh_unsub.pop(node_id)()

        self._device_refresh_unsub[node_id] = async_track_time_interval(
            self.hass,
            self._async_refresh_device,
            timedelta(seconds=interval),
        )

        if self._device_update_intervals:
            self.update_interval = timedelta(
                seconds=min(self._device_update_intervals.values(), default=self.poll_interval)
            )

    @callback
    def _async_refresh_device(self, _now: Any) -> None:
        """Trigger a refresh when a device-specific interval is reached."""
        self.hass.async_create_task(self.async_request_refresh())

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            devices = await self.api.get_devices()
        except APIAuthError as err:
            LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        for device in devices:
            node_id = device.get("nodeId")
            if not node_id:
                continue

            current_interval = self._device_update_intervals.get(node_id)
            api_interval = device.get("update_interval")

            if current_interval is None and api_interval is not None:
                interval = int(api_interval)
            elif current_interval is not None:
                interval = current_interval
            else:
                interval = self.poll_interval

            self._device_update_intervals[node_id] = interval
            device["update_interval"] = interval
            self._reschedule_device_update(node_id, interval)

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return devices

    # ----------------------------------------------------------------------------
    # Here we add some custom functions on our data coordinator to be called
    # from entity platforms to get access to the specific data they want.
    #
    # These will be specific to your api or yo may not need them at all
    # ----------------------------------------------------------------------------
    def get_device(self, device_id: str) -> dict[str, Any]:
        """Get a device entity from our api data using the device_id."""
        try:
            return [
                devices for devices in self.data if devices["deviceId"] == device_id
            ][0]
        except (TypeError, IndexError):
            # In this case if the device id does not exist you will get an IndexError.
            # If api did not return any data, you will get TypeError.
            return None
        
    def get_node(self, node_id: str) -> dict[str, Any]:
        """Get a device entity from our api data using the node_id."""
        try:
            return [
                devices for devices in self.data if devices["nodeId"] == node_id
            ][0]
        except (TypeError, IndexError):
            # In this case if the device id does not exist you will get an IndexError.
            # If api did not return any data, you will get TypeError.
            return None

    def get_device_parameter(self, node_id: str, parameter: str) -> Any:
        """Get the parameter value of one of our devices from our api data."""
        if device := self.get_node(node_id):
            return device.get(parameter)
        
    def get_device_capability_parameter(self, node_id: str, capability: ENKI_CAPABILITY, parameter: str | None = None, in_last_reported_value: bool = True):
        if not (device := self.get_node(node_id)):
            return
        dc = device.get(capability.name, None)
        if not dc:
            return
        if in_last_reported_value:
            dc = dc.get('lastReportedValue', None)
        if not dc:
            return
        if not parameter:
            return dc
        return dc.get(parameter, None)
            
    
    def update_data(self, node_id: str, updated_values: dict[str, Any]) -> None:
        """Update device attribute.

        Support nested dictionaries so we can merge dict of dict updates into
        the existing device data.
        """
        device = self.get_node(node_id)
        if not isinstance(device, dict):
            return

        def _merge_dicts(target: dict[str, Any], updates: dict[str, Any]) -> None:
            for key, value in updates.items():
                if isinstance(value, dict) and isinstance(target.get(key), dict):
                    _merge_dicts(target[key], value)
                else:
                    target[key] = value

        _merge_dicts(device, updated_values)
        self.async_set_updated_data(self.data)

    def update_endpoint_power(self, node_id: int, endpoint_id: int, power: str) -> None:
        """Optimistically update power state for a specific electricalEndpoints entry."""
        device = self.get_node(node_id)
        endpoints = device.get(ENKI_CHECK_ELECTRICAL_POWER.name).get('endpoints', [])
        if isinstance(endpoints, list):
            for ep in endpoints:
                if not isinstance(ep, dict):
                    continue
                if ep.get("id") == endpoint_id:
                    ep["lastReportedValue"] = power
                    break
        self.async_set_updated_data(self.data)
