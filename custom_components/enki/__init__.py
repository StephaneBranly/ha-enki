"""The Integration 101 Template integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .coordinator import EnkiCoordinator

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.FAN, Platform.SENSOR, Platform.SWITCH, Platform.BINARY_SENSOR, Platform.NUMBER, Platform.BUTTON, Platform.COVER, Platform.SELECT, Platform.ALARM_CONTROL_PANEL]


@dataclass
class RuntimeData:
    """Class to hold your data."""

    coordinator: DataUpdateCoordinator


EnkiConfigEntry = ConfigEntry[RuntimeData]


from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, LOGGER
from .coordinator import EnkiCoordinator

async def _create_gateways(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    coordinator: EnkiCoordinator,
) -> None:
    """Create Enki gateway devices."""

    device_registry = dr.async_get(hass)

    for device in coordinator.data:
        if device.get("deviceType") != "gateways":
            continue

        gateway_id = device.get("nodeId")
        
        if not gateway_id:
            continue
        model = device.get(
                "modelNumber",
                "Enki",
            )
        manufacturer = device.get(
                "manufacturerId",
                "Enki",
            )
        if not model:
            model = device.get(
                "i18n",
                "Enki",
            )
            if model:
                model = model.replace(f"{manufacturer.lower()}_", "")
                model = model.replace('tr_device_', '')
                model = model.replace('_label', '')
                model = model.replace("_", " ")
                model = model.title()
            else:
                model = 'Unknown'
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(DOMAIN, gateway_id)},
            manufacturer=manufacturer,
            name=device.get(
                "deviceName",
                "Enki Connect Box",
            ),
            model=model,
            sw_version=device.get("version"),
            serial_number=device.get(
                "serialNumber"
            ),
        )

        LOGGER.debug(
            "Created gateway device %s",
            gateway_id,
        )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
) -> bool:
    """Set up Enki from a config entry."""

    LOGGER.info(
        "Setting up Enki integration for %s",
        config_entry.title,
    )

    coordinator = EnkiCoordinator(
        hass,
        config_entry,
    )

    await coordinator.async_config_entry_first_refresh()

    if not await coordinator.api.check_connected():
        raise ConfigEntryNotReady

    config_entry.async_on_unload(
        config_entry.add_update_listener(
            _async_update_listener
        )
    )

    config_entry.runtime_data = RuntimeData(
        coordinator
    )

    #
    # Create Enki gateways before entities
    #
    await _create_gateways(
        hass,
        config_entry,
        coordinator,
    )

    #
    # Setup entity platforms
    #
    await hass.config_entries.async_forward_entry_setups(
        config_entry,
        PLATFORMS,
    )

    LOGGER.info(
        "Enki integration loaded successfully. "
        "%s devices discovered.",
        len(coordinator.data),
    )

    return True

async def _async_update_listener(hass: HomeAssistant, config_entry):
    """Handle config options update."""
    # Reload the integration when the options change.
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Delete device if selected from UI."""
    # Adding this function shows the delete device option in the UI.
    # Remove this function if you do not want that option.
    # You may need to do some checks here before allowing devices to be removed.
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: EnkiConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when you remove your integration or shutdown HA.
    # If you have created any custom services, they need to be removed here too.

    # Unload platforms and return result
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
