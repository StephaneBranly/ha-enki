"""Data update coordinator for a single Enki device."""
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import DOMAIN, HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API, APIAuthError
from .const import ENKI_CAPABILITY, ENKI_CHECK_ELECTRICAL_POWER, LOGGER

class EnkiCoordinator(DataUpdateCoordinator):
    """Coordinate refreshes for one Enki device."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: API,
        device: dict[str, Any],
        interval: int,
        interval_overrides: int,
        interval_store: Store,
    ) -> None:
        """Initialize a coordinator dedicated to one device."""
        self.device = device
        self.node_id = str(device["nodeId"])
        self.api = api
        self.poll_interval = interval
        self._device_interval_overrides = interval_overrides
        self._device_interval_store = interval_store
        self._device_refresh_unsub = None

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN} ({self.node_id})",
            update_method=self.async_update_data,
            update_interval=None,
        )
        self._reschedule_device_update(interval)

    async def _async_save_device_update_intervals(self) -> None:
        """Save user-configured device intervals to Home Assistant storage."""
        await self._device_interval_store.async_save(self._device_interval_overrides)

    def get_device_update_interval(self) -> int:
        """Return the refresh interval configured for a given device."""
        return int(self.device.get("update_interval", self.poll_interval))

    def set_device_update_interval(self, seconds: float) -> None:
        """Update the refresh interval for a specific device and reschedule it."""
        interval = max(10, int(seconds))
        self.device["update_interval"] = interval
        self._device_interval_overrides = interval
        self.poll_interval = interval
        self._reschedule_device_update(interval)
        self.hass.async_create_task(self._async_save_device_update_intervals())

    @callback
    def _reschedule_device_update(self, interval: int) -> None:
        """Restart this device's scheduled refresh with a new cadence."""
        if self._device_refresh_unsub is not None:
            self._device_refresh_unsub()

        self._device_refresh_unsub = async_track_time_interval(
            self.hass,
            self._async_refresh_device,
            timedelta(seconds=interval),
        )

    @callback
    def shutdown(self) -> None:
        """Stop the device refresh timer when the config entry unloads."""
        if self._device_refresh_unsub is not None:
            self._device_refresh_unsub()
            self._device_refresh_unsub = None

    @callback
    def _async_refresh_device(self, _now: Any) -> None:
        """Trigger a refresh when a device-specific interval is reached."""
        LOGGER.debug("Refreshing device data for node_id: %s", self.node_id)
        self.hass.async_create_task(self.async_request_refresh())

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            self.device = await self.api.refresh_node(self.device)
            LOGGER.debug("Refreshed device from API: %s", self.node_id)
        except APIAuthError as err:
            LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        self.device["update_interval"] = self.poll_interval
        return self.device

    # ----------------------------------------------------------------------------
    # Here we add some custom functions on our data coordinator to be called
    # from entity platforms to get access to the specific data they want.
    #
    # These will be specific to your api or yo may not need them at all
    # ----------------------------------------------------------------------------
    def get_device(self) -> dict[str, Any]:
        return self.device
        
    def get_device_parameter(self, parameter: str) -> Any:
        """Get the parameter value of one of our devices from our api data."""
        return self.device.get(parameter)
        
    def get_device_capability_parameter(self, capability: ENKI_CAPABILITY, parameter: str | None = None, in_last_reported_value: bool = True):
        dc = self.device.get(capability.name, None)
        if not dc:
            return
        if in_last_reported_value:
            dc = dc.get('lastReportedValue', None)
        if not dc:
            return
        if not parameter:
            return dc
        return dc.get(parameter, None)
            
    
    def update_data(self, updated_values: dict[str, Any]) -> None:
        """Update device attribute.

        Support nested dictionaries so we can merge dict of dict updates into
        the existing device data.
        """
        device = self.get_device()
        if not isinstance(device, dict):
            return

        def _merge_dicts(target: dict[str, Any], updates: dict[str, Any]) -> None:
            for key, value in updates.items():
                if isinstance(value, dict) and isinstance(target.get(key), dict):
                    _merge_dicts(target[key], value)
                else:
                    target[key] = value

        _merge_dicts(device, updated_values)
        self.async_set_updated_data(device)

    def update_endpoint_power(self, endpoint_id: int, power: str) -> None:
        """Optimistically update power state for a specific electricalEndpoints entry."""
        endpoints = self.device.get(ENKI_CHECK_ELECTRICAL_POWER.name).get('endpoints', [])
        if isinstance(endpoints, list):
            for ep in endpoints:
                if not isinstance(ep, dict):
                    continue
                if ep.get("id") == endpoint_id:
                    ep["lastReportedValue"] = power
                    break
        self.async_set_updated_data(self.device)
