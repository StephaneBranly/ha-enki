"""Enki API."""

from __future__ import annotations

import aiohttp
import asyncio
import logging
from dataclasses import dataclass
from typing import Any
import time
import re

from .const import (
    ENKI_BFF_ITEMS,
    ENKI_CAPABILITY,
    ENKI_HOMES_LIST,
    ENKI_NODE_CAPABILITY,
    LOGGER,
    ENKI_OIDC_URL,
    ENKI_URL,
    ENKI_REFERENTIEL_API_KEY,
    ENKI_POWER_API_KEY,
    ENKI_BATTERY_HEALTH_API_KEY)

proxy = None

@dataclass
class Device:
    """API device."""
    home_id: str
    device_id: str #device_id represents the type of device used (Hw reference)
    node_id: str #node_id represents the physical device (toke,)
    device_name: str

class API:
    """Class for Enki API."""

    def __init__(self, user: str, pwd: str) -> None:
        """Initialise."""
        self.user = user
        self.pwd = pwd

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.user

    async def check_connected(self) -> bool:
        """Tell if token is still valid"""
        if not hasattr(self, '_access_token') or time.time()>self._tokenExpiresTime:
            await self.connect()
        return True

    async def connect(self) -> bool:
        """Connect to the Enki API."""
        try:
            async with aiohttp.ClientSession() as session, session.request(
                method="POST",
                url=ENKI_OIDC_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type":"password",
                    "client_id": "enki-front",
                    "username": self.user,
                    "password": self.pwd},
                proxy=proxy,) as resp:

                    if resp.status == 200:
                        response = await resp.json()
                        LOGGER.debug("connect : " + str(response))
                        self._access_token = response["access_token"]
                        self._refresh_token = response["refresh_token"]
                        self._token_type = response["token_type"]
                        tokenExpiresTime = time.time() + response["expires_in"]
                        self._tokenExpiresTime = tokenExpiresTime
                        return True
                    else:
                        response = await resp.text()
                        LOGGER.error("Error connecting to api. status %s, response %s", resp.status, str(response))
                        raise APIAuthError("Error connecting to api. Invalid username or password.")
        except APIAuthError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise APIConnectionError("Error connecting to api : " + repr(err)) from err
        except Exception as err:
            raise APIConnectionError("Unexpected error connecting to api : " + repr(err)) from err

# *******************************************************
    async def get_homes(self):
        """Get list of homes."""
        response = await self.query_endpoint(None, None, ENKI_HOMES_LIST)
        homes = []
        for home in response["items"]:
            homes.append(home["id"])
        return homes

    def merge_properties(self, device: dict[str, Any], properties: dict[str, Any] | None) -> None:
        LOGGER.debug('updating properties for device')
        if not properties:
            return
        for prop in properties:
            if prop != "id":
                device[prop] = properties[prop]

    @staticmethod
    def _parse_sensor_value(description: dict[str, Any] | None) -> float | None:
        """Parse value from sensor description.value (e.g. '109 W' -> 109.0)."""
        if not description or not isinstance(description, dict):
            return None
        value_str = description.get("value")
        if not isinstance(value_str, str):
            return None
        pattern = r"[+-]?[0-9]+\.[0-9]+"
        match = re.search(pattern, value_str)
        if not match:
            return None
        try:
            return float(match.group(0))
        except ValueError:
            return None

    async def get_items_in_section_for_home(self, home_id) -> list[dict[str, Any]]:
        """Get sections in home."""
        devices = []
        response = await self.query_endpoint(home_id, None, ENKI_BFF_ITEMS)
           
        for section in response["sections"]:
            for item in section["items"]:
                if 'deviceId' not in item["metadata"].keys():
                    continue

                device = {
                    "homeId": home_id,
                    "deviceId": item["metadata"]["deviceId"],
                    "nodeId": item["metadata"]["nodeId"],
                    "deviceType": item["metadata"].get("deviceType"),
                    "mainChangeCapabilityId": item["metadata"].get("mainChangeCapabilityId"),
                    "mainCheckCapabilityId": item["metadata"].get("mainCheckCapabilityId"),
                    "mainChangeCapabilityEndpoints": [
                        endpoint.get("id")
                        for endpoint in item["metadata"].get("mainChangeCapability", {}).get("endpoints", [])
                        if endpoint.get("id") is not None
                    ] if item["metadata"].get("mainChangeCapability") is not None else [],
                    "deviceName": item["title"]["label"],
                    "state": item["state"],
                    "isEnabled": item["isEnabled"],
                    "descriptionValue": self._parse_sensor_value(item.get("description"))
                }
                
                devices.append(device)

                node_info = await self.get_node(home_id, device.get("nodeId"))
                self.merge_properties(device, node_info)

                await self.refresh_node(device)
        return devices
        
    async def refresh_node(self, device): 
        """Update device details"""

        home_id = device.get('homeId', None)
        node_id = device.get('nodeId', None)
        
        node_info = await self.get_node(home_id, node_id)
        self.merge_properties(device, node_info)

        if not device.get("isEnabled"):
            return device
        
        device_info = await self.get_device(device.get("deviceId"))
        self.merge_properties(device, device_info)

        capabilities = _capabilities_set(device)
        possible_values = _possible_values_dict(device)

        for enki_capability in ENKI_CAPABILITY.__subclasses__():
            if enki_capability.name in capabilities and self.get_method(enki_capability) == 'get':
                LOGGER.debug(f"auto check : {enki_capability}")
                values = await self.query_endpoint(device.get("homeId"), device.get("nodeId"), enki_capability)
                self.merge_properties(device, {enki_capability.name: values})

        # to do, revoir cette partie refresh device
        if _supports_electrical_power(capabilities, possible_values):
            power_details = await self.get_electrical_power_details(home_id, node_id)
            self.merge_properties(device, {
                "electricalPower": power_details.get("lastReportedValue"),
                "electricalEndpoints": power_details.get("endpoints", []),
            })

        # if "check_battery_health" in capabilities or "check_battery_health" in possible_values:
        #     battery_health = await self._check_battery_health(home_id, node_id)
        #     self.merge_properties(device, {"batteryHealthValue": battery_health})
        return device

    async def get_node(self, home_id, node_id):
        """Get details on a node."""
        return await self.query_endpoint(home_id, node_id, ENKI_NODE_CAPABILITY)

    async def get_device(self, id):
        """Get details on a device."""
        await self.check_connected()
        async with aiohttp.ClientSession() as session, session.request(
            method="GET",
            url=f"{ENKI_URL}/api-enki-referentiel-agg-prod/v1/devices/{id}",
            headers={"Authorization": f"{self._token_type} {self._access_token}",
                    "X-Gateway-APIKey": ENKI_REFERENTIEL_API_KEY},
            proxy=proxy,) as resp:

                if resp.status == 200:
                    response = await resp.json()
                    return response

                else:
                    response = await resp.text()
                    if resp.status == 404:
                        LOGGER.debug("Device not found on get_device. status %s, response %s", resp.status, str(response))
                        return {}
                    LOGGER.error("Error on get_device. status %s, response %s", resp.status, str(response))
                    raise ValueError("bad credentials")
                
    def get_api_name(self, capability: ENKI_CAPABILITY):
        if capability.api_name:
            return capability.api_name
        if capability.name is None:
            return None
        return capability.name.replace('_', '-')
    
    def get_method(self, capability: ENKI_CAPABILITY):
        if capability.method:
            return capability.method
        if not capability.name:
            return 'get'
        if capability.name.__contains__('check'):
            return 'get'
        if capability.name.__contains__('change'):
            return 'post'
        return 'get'
    
    def get_full_endpoint(self, capability: ENKI_CAPABILITY, home_id: str | None, node_id: str | None):
        endpoint_path = capability.endpoint.path
        if capability_name := self.get_api_name(capability):
            endpoint_path = endpoint_path.replace('<capability>', capability_name)
        if home_id:
            endpoint_path = endpoint_path.replace('<home_id>', home_id)
        if node_id:
            endpoint_path = endpoint_path.replace('<node_id>', node_id)
        return f"{ENKI_URL}{endpoint_path}"

    async def query_endpoint(self, home_id: str | None, node_id: str | None, capability: ENKI_CAPABILITY, data: dict | None = None, get_previous_value: ENKI_CAPABILITY | None = None):
        await self.check_connected()
        endpoint_url = self.get_full_endpoint(capability, home_id, node_id)

        if get_previous_value is not None and data is not None:
            new_data = (await self.query_endpoint(home_id, node_id, get_previous_value)).get("lastReportedValue", {})
            new_data.update(data)
            data = new_data

        method = self.get_method(capability)
        LOGGER.debug(f"{endpoint_url}, {capability}, {data}, {method}")
        headers = {
            "Authorization": f"{self._token_type} {self._access_token}",
            "X-Gateway-APIKey": capability.endpoint.x_api_key,
        }
        if home_id:
            headers['homeId'] = home_id
        async with aiohttp.ClientSession() as session, session.request(
             method=method,
             url=endpoint_url,
             headers=headers,
             proxy=proxy,
             json=data) as resp:
                if resp.ok:
                    if method == 'get':
                        response = await resp.json()
                    else:
                        response = await resp.text()
                    return response
                    
                else:
                    response = await resp.text()
                    if resp.status == 404:
                        # to do log
                        return {}
                    # to do meilleur retour
                    LOGGER.error(f"Error on {capability.name}. status {resp.status}, response {str(response)}")
                    raise ValueError("bad credentials") # to do, revoir cette valeur de retour
    
    async def get_electrical_power_details(self, home_id, node_id):
        """Get electrical power state and endpoint states."""
        await self.check_connected()
        async with aiohttp.ClientSession() as session, session.request(
            method="GET",
            url=f"{ENKI_URL}/api-enki-power-prod/v1/power/{node_id}/check-electrical-power",
            headers={
                "Authorization": f"{self._token_type} {self._access_token}",
                "homeId": home_id,
                "X-Gateway-APIKey": ENKI_POWER_API_KEY,
            },
            proxy=proxy,
        ) as resp:
            if resp.status == 200:
                return await resp.json()

            response = await resp.text()
            if resp.status == 404:
                LOGGER.warning("Power endpoint not found. status %s, response %s", resp.status, str(response))
                return {}
            LOGGER.error("Error on power check. status %s, response %s", resp.status, str(response))
            raise ValueError("bad credentials")

    async def _check_battery_health(self, home_id, node_id):
        """Read battery health value from one check endpoint."""
        await self.check_connected()
        async with aiohttp.ClientSession() as session, session.request(
            method="GET",
            url=f"{ENKI_URL}/api-enki-battery-health-prod/v1/sensors/{node_id}/check-battery-health",
            headers={
                "Authorization": f"{self._token_type} {self._access_token}",
                "homeId": home_id,
                "X-Gateway-APIKey": ENKI_BATTERY_HEALTH_API_KEY,
            },
            proxy=proxy,
        ) as resp:
            if resp.status == 200:
                response = await resp.json()
                value = response.get("lastReportedValue")
                LOGGER.debug("Battery health value : %s", response)
                return {
                    "GOOD": 80,
                    "LOW": 30,
                    "LOW_INTERNAL_BATTERY_OF_DEVICE": 30,
                    "REPLACE": 1,
                    "UNKNOWN": None,
                    "CRITICAL": 5
                }.get(value, None)

            response = await resp.text()
            if resp.status == 404:
                LOGGER.warning("Sensor endpoint not found on %s. status %s, response %s", resp.status, str(response))
                return None
            LOGGER.error("Error on sensor check %s. status %s, response %s", resp.status, str(response))
            raise ValueError("bad credentials")

    async def switch_electrical_power(self, home_id, node_id, value):
        """Switch electrical power globally."""
        await self.check_connected()
        payload = {"value": value}

        before_state = None
        if LOGGER.isEnabledFor(logging.DEBUG):
            try:
                before_state = await self.get_electrical_power_details(home_id, node_id)
            except Exception as err:
                before_state = {"error": repr(err)}

        LOGGER.info(
            "Calling switch-electrical-power for node %s (home %s) payload=%s",
            node_id,
            home_id,
            payload,
        )
        headers = {
            "Authorization": f"{self._token_type} {self._access_token}",
            "X-Gateway-APIKey": ENKI_POWER_API_KEY,
        }
        if home_id:
            headers['homeId'] = home_id
        async with aiohttp.ClientSession() as session, session.request(
            method="POST",
            url=f"{ENKI_URL}/api-enki-power-prod/v1/power/{node_id}/switch-electrical-power",
            headers=headers,
            proxy=proxy,
            json=payload,
        ) as resp:
            if resp.status == 202:
                return

            response = await resp.text()
            LOGGER.error("Error on power switch. status %s, response %s", resp.status, str(response))
            raise ValueError("bad credentials")

# *******************************************************

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get devices on api."""
        homes = await self.get_homes()
        devices = []
        for home in homes:
            devices.extend(await self.get_items_in_section_for_home(home))

        return devices

class APIAuthError(Exception):
    """Exception class for auth error."""

class APIConnectionError(Exception):
    """Exception class for connection error."""


def _capabilities_set(device: dict[str, Any]) -> set[str]:
    """Return capabilities as a normalized string set."""
    capabilities = device.get("capabilities")
    if isinstance(capabilities, list):
        return {capability for capability in capabilities if isinstance(capability, str)}
    if isinstance(capabilities, dict):
        return set(capabilities.keys())
    return set()


def _possible_values_dict(device: dict[str, Any]) -> dict[str, Any]:
    """Return possibleValues metadata as a dict if available."""
    possible_values = device.get("possibleValues")
    if isinstance(possible_values, dict):
        return possible_values
    return {}

def _supports_electrical_power(capabilities: set[str], possible_values: dict[str, Any]) -> bool:
    """Tell whether electrical power check/change exists in metadata."""
    return (
        "switch_electrical_power" in capabilities
        or "check_electrical_power" in capabilities
        or "switch_electrical_power" in possible_values
        or "check_electrical_power" in possible_values
    )


def _supports_fan_speed(capabilities: set[str], possible_values: dict[str, Any]) -> bool:
    """Tell whether fan speed control exists in metadata."""
    return (
        "change_fan_speed" in capabilities
        or "check_fan_speed" in capabilities
        or "change_fan_speed" in possible_values
        or "check_fan_speed" in possible_values
    )


def _supports_fan_rotation_direction(capabilities: set[str], possible_values: dict[str, Any]) -> bool:
    """Tell whether fan rotation direction exists in metadata."""
    return (
        "change_fan_rotation_direction" in capabilities
        or "check_fan_rotation_direction" in capabilities
        or "change_fan_rotation_direction" in possible_values
        or "check_fan_rotation_direction" in possible_values
    )


def _supports_airflow_mode(capabilities: set[str], possible_values: dict[str, Any]) -> bool:
    """Tell whether airflow mode exists in metadata."""
    return (
        "change_airflow_mode" in capabilities
        or "check_airflow_mode" in capabilities
        or "change_airflow_mode" in possible_values
        or "check_airflow_mode" in possible_values
    )
