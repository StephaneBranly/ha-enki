"""Cover (roller shutter) setup for Enki integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.enki.const import (
    ENKI_CHANGE_SHUTTER_POSITION,
    ENKI_CHECK_ROLLER_SHUTTER_STATE,
    ENKI_STOP_CHANGE_SHUTTER_POSITION,
)

from . import EnkiConfigEntry
from .base import EnkiBaseEntity
from .coordinator import EnkiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up cover entities."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    covers = [
        EnkiCover(coordinator, device)
        for device in coordinator.data
        if _is_cover_device(device)
    ]

    async_add_entities(covers)


class EnkiCover(EnkiBaseEntity, CoverEntity):
    """Representation of an Enki roller shutter.

    Enki reports the position as a 0-100 percentage where 0 = closed and
    100 = open, which matches Home Assistant's cover convention directly.
    """

    _attr_device_class = CoverDeviceClass.SHUTTER

    def __init__(self, coordinator: EnkiCoordinator, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device)
        self.parameter = "cover"

        capabilities = _capabilities_set(device)
        self._supports_position = "change_shutter_position" in capabilities
        self._supports_stop = "stop_change_shutter_position" in capabilities

        features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
        if self._supports_position:
            features |= CoverEntityFeature.SET_POSITION
        if self._supports_stop:
            features |= CoverEntityFeature.STOP
        self._attr_supported_features = features

    def _shutter_field(self, field: str) -> Any:
        """Read a field from check_roller_shutter_state.lastReportedValue."""
        return self.coordinator.get_device_capability_parameter(
            self.node_id, ENKI_CHECK_ROLLER_SHUTTER_STATE, field
        )

    @property
    def current_cover_position(self) -> int | None:
        """Return current position, 0 (closed) to 100 (open)."""
        position = self._shutter_field("shutterPosition")
        if position is None:
            return None
        return max(0, min(100, int(round(position))))

    @property
    def is_closed(self) -> bool | None:
        """Return True if the shutter is fully closed."""
        opening = self._shutter_field("shutterOpening")
        if isinstance(opening, str):
            return opening.upper() == "CLOSED"
        position = self.current_cover_position
        if position is None:
            return None
        return position <= 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the shutter fully."""
        await self._set_position(100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the shutter fully."""
        await self._set_position(0)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the shutter to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        if position is None:
            return
        await self._set_position(int(position))

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop an in-progress shutter movement."""
        if not self._supports_stop:
            return
        await self.coordinator.api.query_endpoint(
            self.device["homeId"], self.node_id, ENKI_STOP_CHANGE_SHUTTER_POSITION
        )

    async def _set_position(self, position: int) -> None:
        """Send a position command and optimistically update the cache."""
        clamped = max(0, min(100, position))
        await self.coordinator.api.query_endpoint(
            self.device["homeId"],
            self.node_id,
            ENKI_CHANGE_SHUTTER_POSITION,
            {"value": clamped},
        )
        self.coordinator.update_data(
            self.node_id,
            {ENKI_CHECK_ROLLER_SHUTTER_STATE.name: {"lastReportedValue": {"shutterPosition": clamped}}},
        )


def _capabilities_set(device: dict[str, Any]) -> set[str]:
    """Return capabilities as a normalized string set."""
    capabilities = device.get("capabilities")
    if isinstance(capabilities, list):
        return {capability for capability in capabilities if isinstance(capability, str)}
    if isinstance(capabilities, dict):
        return set(capabilities.keys())
    return set()


def _is_cover_device(device: dict[str, Any]) -> bool:
    """Detect roller shutter devices from capabilities metadata."""
    capabilities = _capabilities_set(device)
    return (
        "change_shutter_position" in capabilities
        or "check_roller_shutter_state" in capabilities
    )
