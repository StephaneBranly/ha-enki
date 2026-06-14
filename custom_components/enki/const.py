"""Constants for Enki integration."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "enki"
NAME = "Enki"

DEFAULT_SCAN_INTERVAL = 60

ENKI_OIDC_URL = "https://keycloak-prod.iot.leroymerlin.fr/realms/enki/protocol/openid-connect/token"
ENKI_URL = "https://enki.api.devportal.adeo.cloud"
ENKI_HOME_API_KEY = "FULsxyI3x1f7MtLVOsP6V1DeAPmBQJCB"
ENKI_BFF_API_KEY = "Bco7qBHRHOQiSVcEHdgS0rijpebMBwkB"
ENKI_NODE_API_KEY = "UBb0Kv6xXpG6bOvD8VZ9A63uxqQ4G1A3"
ENKI_REFERENTIEL_API_KEY = "3uk9rlaIUgBsz1tEPV7GQMhhGfRwPFJY"
ENKI_AIRFLOW_API_KEY = "hder4GeBrdbzQlV2R22dm2a9pbfTTHPj"
ENKI_POWER_API_KEY = "DZ9MSuTT7sQxJWxxkBokAGvIt57qVl9N"
ENKI_BATTERY_HEALTH_API_KEY = "WcydJ76nQUo8AiwkV05kn3kiNyM31b3M"

class ENKI_ENDPOINT:
    path: str | None = None
    x_api_key: str | None = None

class ENKI_LIGHTS_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-lighting-prod/v1/lighting/<node_id>/<capability>'
    x_api_key = "3OVsNulRsUXfr7Hze54OHx8l6qDu2UcE"

class ENKI_TEMPERATURE_HUMIDITY_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-temperature-humidity-sensor-prod/v1/sensors/<node_id>/<capability>'
    x_api_key = "V6mMQHQAGNNVwjhuBXlVhQNYzZOxARJ3"

class ENKI_CAPABILITIY:
    name: str | None = None
    api_name: str | None = None
    method: str | None = None
    endpoint: ENKI_ENDPOINT | None = None


class ENKI_CHECK_LIGHT_STATE(ENKI_CAPABILITIY):
    name = 'check_light_state'
    endpoint = ENKI_LIGHTS_ENDPOINT

class ENKI_CHANGE_LIGHT_STATE(ENKI_CAPABILITIY):
    name = 'change_light_state'
    endpoint = ENKI_LIGHTS_ENDPOINT

class ENKI_CHECK_CURRENT_TEMPERATURE(ENKI_CAPABILITIY):
    name = 'check_current_temperature'
    endpoint = ENKI_TEMPERATURE_HUMIDITY_ENDPOINT

class ENKI_CHECK_CURRENT_HUMIDITY(ENKI_CAPABILITIY):
    name = 'check_current_humidity'
    endpoint = ENKI_TEMPERATURE_HUMIDITY_ENDPOINT