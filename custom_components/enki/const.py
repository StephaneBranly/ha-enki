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

class ENKI_ENDPOINT:
    path: str = None
    x_api_key: str = None

class ENKI_CAPABILITY(ENKI_ENDPOINT):
    name: str = None
    api_name: str = None
    method: str = None
    coverage: int = 100


### HOME

class ENKI_HOMES_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-home-prod/v1/homes'
    x_api_key = "FULsxyI3x1f7MtLVOsP6V1DeAPmBQJCB"

class ENKI_HOMES_LIST(ENKI_CAPABILITY, ENKI_HOMES_ENDPOINT):
    _ = None

### BFF
class ENKI_BFF_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-mobile-bff-prod/v1/dashboard/homes/<home_id>?hasGroups=true'
    x_api_key = "Bco7qBHRHOQiSVcEHdgS0rijpebMBwkB"

class ENKI_BFF_ITEMS(ENKI_CAPABILITY, ENKI_BFF_ENDPOINT):
    _ = None

### NODE

class ENKI_NODE_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-node-agg-prod/v1/nodes/<node_id>'
    x_api_key = 'UBb0Kv6xXpG6bOvD8VZ9A63uxqQ4G1A3'

class ENKI_NODE_CAPABILITY(ENKI_CAPABILITY, ENKI_NODE_ENDPOINT):
    _ = None
### LIGHTS
class ENKI_LIGHTS_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-lighting-prod/v1/lighting/<node_id>/<capability>'
    x_api_key = "3OVsNulRsUXfr7Hze54OHx8l6qDu2UcE"

class ENKI_CHANGE_LIGHT_STATE(ENKI_CAPABILITY, ENKI_LIGHTS_ENDPOINT):
    name = 'change_light_state'

class ENKI_CHECK_LIGHT_STATE(ENKI_CAPABILITY, ENKI_LIGHTS_ENDPOINT):
    name = 'check_light_state'

### TEMPERATURE HUMIDTY

class ENKI_TEMPERATURE_HUMIDITY_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-temperature-humidity-sensor-prod/v1/sensors/<node_id>/<capability>'
    x_api_key = "V6mMQHQAGNNVwjhuBXlVhQNYzZOxARJ3"

class ENKI_CHECK_CURRENT_TEMPERATURE(ENKI_CAPABILITY, ENKI_TEMPERATURE_HUMIDITY_ENDPOINT):
    name = 'check_current_temperature'

class ENKI_CHECK_CURRENT_HUMIDITY(ENKI_CAPABILITY, ENKI_TEMPERATURE_HUMIDITY_ENDPOINT):
    name = 'check_current_humidity'

### AIRFLOW

class ENKI_AIRFLOW_ENDPOINT(ENKI_ENDPOINT):
    path = "/api-enki-airflow-prod/v1/airflow/<node_id>/<capability>"
    x_api_key = "hder4GeBrdbzQlV2R22dm2a9pbfTTHPj"

class ENKI_CHECK_FAN_SPEED(ENKI_CAPABILITY, ENKI_AIRFLOW_ENDPOINT):
    name = 'check_fan_speed'

class ENKI_CHECK_FAN_ROTATION_DIRECTION(ENKI_CAPABILITY, ENKI_AIRFLOW_ENDPOINT):
    name = 'check_fan_rotation_direction'

class ENKI_CHECK_AIRFLOW_MODE(ENKI_CAPABILITY, ENKI_AIRFLOW_ENDPOINT):
    name = 'check_airflow_mode'

class ENKI_CHANGE_FAN_SPEED(ENKI_CAPABILITY, ENKI_AIRFLOW_ENDPOINT):
    name = 'change_fan_speed'

class ENKI_CHANGE_FAN_ROTATION_DIRECTION(ENKI_CAPABILITY, ENKI_AIRFLOW_ENDPOINT):
    name = 'change_fan_rotation_direction'

class ENKI_CHANGE_AIRFLOW_MODE(ENKI_CAPABILITY, ENKI_AIRFLOW_ENDPOINT):
    name = 'change_airflow_mode'

### POWER

class ENKI_POWER_ENDPOINT(ENKI_ENDPOINT):
    path = '/api-enki-power-prod/v1/power/<node_id>/<capability>'
    x_api_key = 'DZ9MSuTT7sQxJWxxkBokAGvIt57qVl9N'

class ENKI_SWITCH_ELECTRICAL_POWER(ENKI_CAPABILITY, ENKI_POWER_ENDPOINT):
    name = 'switch_electrical_power'

class ENKI_CHECK_ELECTRICAL_POWER(ENKI_CAPABILITY, ENKI_POWER_ENDPOINT):
    name = 'check_electrical_power'

### BATTERY HEALTH

class ENKI_BATTERY_HEALTH_ENDPOINT(ENKI_ENDPOINT):
    path = "/api-enki-battery-health-prod/v1/sensors/<node_id>/<capability>"
    x_api_key = "WcydJ76nQUo8AiwkV05kn3kiNyM31b3M"

class ENKI_CHECK_BATTERY_HEALTH(ENKI_CAPABILITY, ENKI_BATTERY_HEALTH_ENDPOINT):
    name = 'check_battery_health'

### PRESENCE DETECTOR

class ENKI_PRESENCE_DETECTOR_ENDPOINT(ENKI_ENDPOINT):
    path = "/api-enki-presence-detector-prod/v1/sensors/<node_id>/<capability>"
    x_api_key = "bHEwVewJI2aNUiDX6KXt9ErzazfkarYp"

class ENKI_CHECK_MOTION_DETECTION(ENKI_CAPABILITY, ENKI_PRESENCE_DETECTOR_ENDPOINT):
    name = "check_motion_detection"

class ENKI_CHECK_MOTION_DETECTOR_STATE(ENKI_CAPABILITY, ENKI_PRESENCE_DETECTOR_ENDPOINT):
    name = "check_motion_detector_state"


### CONTACT SENSOR

class ENKI_CONTACT_SENSOR_ENDPOINT(ENKI_ENDPOINT):
    path = "/api-enki-contact-sensor-prod/v1/sensors/<node_id>/<capability>"
    x_api_key = "B2K2xlXnpVGEPylKq0Xn79LRuBG60w30"

class ENKI_CHECK_CONTACT_SENSOR_STATE(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = "check_contact_sensor_state"

class ENKI_CHECK_VIBRATION_DETECTION(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = "check_vibration_detection"

# class ENKI_CHECK_VIBRATION_DETECTOR_STATE(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
#     name = "check_vibration_detector_state"

class ENKI_CHECK_VIBRATION_DETECTION_ACTIVATION(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = 'check_vibration_detection_activation'

class ENKI_ACTIVATE_VIBRATION_DETECTION(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = 'activate_vibration_detection'

class ENKI_CHECK_CONTACT_DETECTION_ACTIVATION(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = 'check_contact_detection_activation'

class ENKI_ACTIVATE_CONTACT_DETECTION(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = 'activate_contact_detection'

class ENKI_CHECK_VIBRATION_SENSIBILITY_LEVEL(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = 'check_vibration_sensibility_level'

class ENKI_CHANGE_VIBRATION_SENSIBILITY_LEVEL(ENKI_CAPABILITY, ENKI_CONTACT_SENSOR_ENDPOINT):
    name = 'change_vibration_sensibility_level'