"""Enki API."""

from __future__ import annotations

import aiohttp
import asyncio
from typing import Any
import time

from .const import (
    ENKI_BFF_ITEMS,
    ENKI_CAPABILITY,
    ENKI_HOMES_LIST,
    ENKI_NODE_CAPABILITY,
    ENKI_SCENARIO_LIST_CAPABILITY,
    LOGGER,
    ENKI_OIDC_URL,
    ENKI_URL,
    ENKI_REFERENTIEL_API_KEY,
)

proxy = None

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
        if not properties:
            return
        for prop in properties:
            if prop != "id":
                device[prop] = properties[prop]

    async def get_items_in_section_for_home(self, home_id) -> list[dict[str, Any]]:
        """Get sections in home."""
        devices = []
        response = await self.query_endpoint(home_id, None, ENKI_BFF_ITEMS)
           
        for section in response["sections"]:
            for item in section["items"]:
                if 'deviceId' not in item["metadata"].keys():
                    continue

                device = {
                    "type": "physicalDevice",
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
                }
                
                devices.append(device)

                node_info = await self.get_node(home_id, device.get("nodeId"))
                self.merge_properties(device, node_info)

                await self.refresh_node(device)
        return devices
        

    async def load_scenarios(self, home_id: str) -> list[dict[str, Any]]:
        """Get scenarios in home."""
        response = await self.query_endpoint(home_id, None, ENKI_SCENARIO_LIST_CAPABILITY)
        scenarios = []
        for item in response.get("items", []):
            scenario = {
                "type": "scenario",
                "homeId": home_id,
                "scenarioId": item.get("scenarioId"),
                "scenarioName": item.get("label"),
                "isEnabled": item.get("enabled"),
            }
            scenarios.append(scenario)
        return scenarios
    
    async def refresh_node(self, device): 
        """Update device details"""

        home_id = device.get('homeId', None)

        if device.get('type', None) != 'physicalDevice':
            return device
        
        node_id = device.get('nodeId', None)
        
        node_info = await self.get_node(home_id, node_id)
        self.merge_properties(device, node_info)

        if not device.get("isEnabled"):
            return device
        
        device_info = await self.get_device(device.get("deviceId"))
        self.merge_properties(device, device_info)

        capabilities = _capabilities_set(device)

        for enki_capability in ENKI_CAPABILITY.__subclasses__():
            if enki_capability.name in capabilities and self.get_method(enki_capability) == 'get':
                values = await self.query_endpoint(device.get("homeId"), device.get("nodeId"), enki_capability)
                self.merge_properties(device, {enki_capability.name: values})

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
        if capability.name.__contains__('switch'):
            return 'post'
        if capability.name.__contains__('activate'):
            return 'post'
        return 'get'
    
    def get_full_endpoint(self, capability: ENKI_CAPABILITY, home_id: str | None, node_id: str | None):
        endpoint_path = capability.path
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

        headers = {
            "Authorization": f"{self._token_type} {self._access_token}",
            "X-Gateway-APIKey": capability.x_api_key,
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

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get devices on api."""
        homes = await self.get_homes()
        devices = []
        for home in homes:
            devices.extend(await self.get_items_in_section_for_home(home))
            devices.extend(await self.load_scenarios(home))

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
