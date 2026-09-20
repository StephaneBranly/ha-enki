
"""Support for Enki alarm panels."""

from __future__ import annotations
from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.enki.base import EnkiBaseEntity

from . import EnkiConfigEntry
from .coordinator import EnkiCoordinator

from .const import ENKI_CHANGE_ALARM_HOME, ENKI_GET_ALARM_STATUS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EnkiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enki alarm panels."""
    coordinator: EnkiCoordinator = config_entry.runtime_data.coordinator

    alarm_control_panels = [
            entity
            for device in coordinator.data
            for entity in _build_alarm_control_panel_entities(coordinator, device)
        ]
    async_add_entities(alarm_control_panels)

class EnkiAlarmControlPanel(
    EnkiBaseEntity,
    AlarmControlPanelEntity,
):
    """Representation of an Enki alarm panel."""

    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_HOME
    )

    def __init__(self, coordinator, device) -> None:
        super().__init__(coordinator, device)
        self._attr_code_arm_required = False

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        """Return current alarm state."""
        threatLevel = self.coordinator.get_device_parameter(self.node_id, ENKI_GET_ALARM_STATUS.name).get('threatLevel')
        currentMode = self.coordinator.get_device_parameter(self.node_id, ENKI_GET_ALARM_STATUS.name).get('currentMode')

        if threatLevel == 'DANGER' and currentMode != 'DISABLED':
            return AlarmControlPanelState.TRIGGERED


        mapping = {
            "FULL": AlarmControlPanelState.ARMED_AWAY,
            "PARTIAL": AlarmControlPanelState.ARMED_HOME,
            "DISABLED": AlarmControlPanelState.DISARMED,
            "PENDING_PARTIAL": AlarmControlPanelState.ARMING,
            "PENDING_FULL": AlarmControlPanelState.ARMING,
        }

        return mapping.get(currentMode)

    async def async_alarm_disarm(self, code=None) -> None:
        """Disarm alarm."""
        await self.coordinator.api.query_endpoint(
                self.device["homeId"],
                self.device["nodeId"],
                ENKI_CHANGE_ALARM_HOME,
                {"currentMode": "DISABLED"},
            )

    async def async_alarm_arm_home(self, code=None) -> None:
        """Arm alarm at home."""

        await self.coordinator.api.query_endpoint(
                        self.device["homeId"],
                        self.device["nodeId"],
                        ENKI_CHANGE_ALARM_HOME,
                        {"currentMode": "PARTIAL"},
                    )

    async def async_alarm_arm_away(self, code=None) -> None:
        """Arm alarm away."""

        await self.coordinator.api.query_endpoint(
            self.device["homeId"],
            self.device["nodeId"],
            ENKI_CHANGE_ALARM_HOME,
            {"currentMode": "FULL"},
        )


def _build_alarm_control_panel_entities(coordinator: EnkiCoordinator, device: dict[str, Any]) -> list[EnkiAlarmControlPanel]:
    """Create power production alarm_control_panel for inverter devices."""

    alarm_control_panels = []

    if device.get("type") != 'security':
        return []
    
    alarm_control_panels.append(
        EnkiAlarmControlPanel(
            coordinator,
            device,
        )
    )

    return alarm_control_panels
