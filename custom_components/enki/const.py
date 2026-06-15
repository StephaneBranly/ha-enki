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
ENKI_REFERENTIEL_API_KEY = "3uk9rlaIUgBsz1tEPV7GQMhhGfRwPFJY"
ENKI_POWER_API_KEY = "DZ9MSuTT7sQxJWxxkBokAGvIt57qVl9N"
ENKI_BATTERY_HEALTH_API_KEY = "WcydJ76nQUo8AiwkV05kn3kiNyM31b3M"

class ENKI_ENDPOINT:
    path: str | None = None
    x_api_key: str | None = None

class ENKI_CAPABILITY:
    name: str | None = None
    api_name: str | None = None
    method: str | None = None
    endpoint: ENKI_ENDPOINT | None = None


### HOME

class ENKI_HOMES_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-home-prod/v1/homes'
    x_api_key = "FULsxyI3x1f7MtLVOsP6V1DeAPmBQJCB"

class ENKI_HOMES_LIST(ENKI_CAPABILITY):
    endpoint = ENKI_HOMES_ENDPOINT

### BFF
class ENKI_BFF_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-mobile-bff-prod/v1/dashboard/homes/<home_id>?hasGroups=true'
    x_api_key = "Bco7qBHRHOQiSVcEHdgS0rijpebMBwkB"

class ENKI_BFF_ITEMS(ENKI_CAPABILITY):
    endpoint = ENKI_BFF_ENDPOINT

### NODE

class ENKI_NODE_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-node-agg-prod/v1/nodes/<node_id>'
    x_api_key = 'UBb0Kv6xXpG6bOvD8VZ9A63uxqQ4G1A3'

class ENKI_NODE_CAPABILITY(ENKI_CAPABILITY):
    endpoint = ENKI_NODE_ENDPOINT

### LIGHTS
class ENKI_LIGHTS_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-lighting-prod/v1/lighting/<node_id>/<capability>'
    x_api_key = "3OVsNulRsUXfr7Hze54OHx8l6qDu2UcE"

class ENKI_CHANGE_LIGHT_STATE(ENKI_CAPABILITY):
    name = 'change_light_state'
    endpoint = ENKI_LIGHTS_ENDPOINT

class ENKI_CHECK_LIGHT_STATE(ENKI_CAPABILITY):
    name = 'check_light_state'
    endpoint = ENKI_LIGHTS_ENDPOINT

### TEMPERATURE HUMIDTY

class ENKI_TEMPERATURE_HUMIDITY_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-temperature-humidity-sensor-prod/v1/sensors/<node_id>/<capability>'
    x_api_key = "V6mMQHQAGNNVwjhuBXlVhQNYzZOxARJ3"

class ENKI_CHECK_CURRENT_TEMPERATURE(ENKI_CAPABILITY):
    name = 'check_current_temperature'
    endpoint = ENKI_TEMPERATURE_HUMIDITY_ENDPOINT

class ENKI_CHECK_CURRENT_HUMIDITY(ENKI_CAPABILITY):
    name = 'check_current_humidity'
    endpoint = ENKI_TEMPERATURE_HUMIDITY_ENDPOINT

### AIRFLOW

class ENKI_AIRFLOW_ENDPOINT(ENKI_ENDPOINT):
    path = "/api-enki-airflow-prod/v1/airflow/<node_id>/<capability>"
    x_api_key = "hder4GeBrdbzQlV2R22dm2a9pbfTTHPj"

class ENKI_CHECK_FAN_SPEED(ENKI_CAPABILITY):
    name = 'check_fan_speed'
    endpoint = ENKI_AIRFLOW_ENDPOINT

class ENKI_CHECK_FAN_ROTATION_DIRECTION(ENKI_CAPABILITY):
    name = 'check_fan_rotation_direction'
    endpoint = ENKI_AIRFLOW_ENDPOINT

class ENKI_CHECK_AIRFLOW_MODE(ENKI_CAPABILITY):
    name = 'check_airflow_mode'
    endpoint = ENKI_AIRFLOW_ENDPOINT

class ENKI_CHANGE_FAN_SPEED(ENKI_CAPABILITY):
    name = 'change_fan_speed'
    endpoint = ENKI_AIRFLOW_ENDPOINT

class ENKI_CHANGE_FAN_ROTATION_DIRECTION(ENKI_CAPABILITY):
    name = 'change_fan_rotation_direction'
    endpoint = ENKI_AIRFLOW_ENDPOINT

class ENKI_CHANGE_AIRFLOW_MODE(ENKI_CAPABILITY):
    name = 'change_airflow_mode'
    endpoint = ENKI_AIRFLOW_ENDPOINT