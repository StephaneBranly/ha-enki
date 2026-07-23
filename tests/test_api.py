"""Tests for the Enki API."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.enki.api import API
from custom_components.enki.const import ENKI_CHECK_LIGHT_STATE


def _session_with_response(*, status, text):
    response = MagicMock()
    response.ok = True
    response.status = status
    response.text = AsyncMock(return_value=text)

    request = MagicMock()
    request.__aenter__ = AsyncMock(return_value=response)
    request.__aexit__ = AsyncMock(return_value=None)

    session = MagicMock()
    session.request.return_value = request

    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=session)
    context.__aexit__ = AsyncMock(return_value=None)
    return context


@pytest.mark.asyncio
async def test_query_endpoint_returns_empty_dict_for_empty_202_response():
    """An empty successful GET response is valid."""
    api = API("user", "password")
    api.check_connected = AsyncMock(return_value=True)
    api._token_type = "Bearer"
    api._access_token = "token"

    with patch(
        "custom_components.enki.api.aiohttp.ClientSession",
        return_value=_session_with_response(status=202, text=""),
    ):
        response = await api.query_endpoint(
            "home-id", "node-id", ENKI_CHECK_LIGHT_STATE
        )

    assert response == {}


@pytest.mark.asyncio
async def test_query_endpoint_decodes_json_without_relying_on_content_type():
    """A successful GET response is decoded from its body."""
    api = API("user", "password")
    api.check_connected = AsyncMock(return_value=True)
    api._token_type = "Bearer"
    api._access_token = "token"

    with patch(
        "custom_components.enki.api.aiohttp.ClientSession",
        return_value=_session_with_response(status=200, text='{"power": "ON"}'),
    ):
        response = await api.query_endpoint(
            "home-id", "node-id", ENKI_CHECK_LIGHT_STATE
        )

    assert response == {"power": "ON"}
