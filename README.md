# Enki integration for Home Assistant (Unofficial)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/StephaneBranly/ha-enki?color=41BDF5&style=for-the-badge)](https://github.com/StephaneBranly/ha-enki/releases/latest)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=StephaneBranly&repository=ha-enki&category=integration)

The unofficial Enki intregration for Home Assistant.

<img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/main/src/icon.png">

> [!NOTE]
> This custom component is relatively new. It does not include all Enki components and may contain bugs.

> [!TIP]
> Quickly test the integration of your current devices with a single Python command! Check Live API test

## Known devices:

<!-- start devices -->
| Name | Image | Id | Coverage (%) | Tested |
|---|---|---|---|---|
|Connected thermometer<br/>Sedea|<img src='./doc/devices/6633842c9f53b36a99838c94.webp'  width='100'/>|*6633842c9f53b36a99838c94*|![100%](https://progress-bar.xyz/100)|✅|
|Outlet 16A, 3680A<br/>Lexman|<img src='./doc/devices/5e258991b472bf9d87b8483f.webp'  width='100'/>|*5e258991b472bf9d87b8483f*|![28%](https://progress-bar.xyz/28)|✅|
|Motion detector<br/>Lexman|<img src='./doc/devices/5e26cc33777472061d55e340.jpg'  width='100'/>|*5e26cc33777472061d55e340*|![100%](https://progress-bar.xyz/100)|✅|
|Water leak detector<br/>Lexman|<img src='./doc/devices/651eada55b3a798ef6b6bc5c.jpg'  width='100'/>|*651eada55b3a798ef6b6bc5c*|![100%](https://progress-bar.xyz/100)|❌|
|ON/OFF relay<br/>Equation|<img src='./doc/devices/63a053851a423d4a245a877c.png'  width='100'/>|*63a053851a423d4a245a877c*|![28%](https://progress-bar.xyz/28)|❌|
|Thermometer with display<br/>Sonoff|<img src='./doc/devices/6634999c9f53b36a99838c95.jpg'  width='100'/>|*6634999c9f53b36a99838c95*|![100%](https://progress-bar.xyz/100)|❌|
|Cadix ceiling fan with light<br/>Inspire|<img src='./doc/devices/6827098c5f52437f08d9d7a1.jpg'  width='100'/>|*6827098c5f52437f08d9d7a1*|![55%](https://progress-bar.xyz/55)|✅|
|Radiator<br/>Noirot|<img src='./doc/devices/67a4b12bae1eca4709a45680.jpg'  width='100'/>|*67a4b12bae1eca4709a45680*|![9%](https://progress-bar.xyz/9)|❌|
|RGB E27 Light<br/>Lexman|<img src='./doc/devices/5d7df749f8bb0659f50d263d.webp'  width='100'/>|*5d7df749f8bb0659f50d263d*|![44%](https://progress-bar.xyz/44)|✅|
|Siren<br/>Lexman|<img src='./doc/devices/5f16c4aca80024b5af0561a1.jpg'  width='100'/>|*5f16c4aca80024b5af0561a1*|![50%](https://progress-bar.xyz/50)|❌|
|Contact detector<br/>Lexman|<img src='./doc/devices/5f1192bc23b5dec92ac93eb4.jpg'  width='100'/>|*5f1192bc23b5dec92ac93eb4*|![90%](https://progress-bar.xyz/90)|✅|
<!-- end -->

<!-- - Eglo V-link tunable white
- Lexman RGBW Light -->

## Supported capabilities

Different device capabilities are curently being integrated to this custom component.

<details>

<summary>Capabilities coverage</summary>

<!-- start capabilities -->
| Capability | Coverage (%) |
|---|---|
|ENKI_HOMES_LIST|![100%](https://progress-bar.xyz/100)|
|ENKI_BFF_ITEMS|![100%](https://progress-bar.xyz/100)|
|ENKI_NODE_CAPABILITY|![100%](https://progress-bar.xyz/100)|
|ENKI_SCENARIO_LIST_CAPABILITY|![100%](https://progress-bar.xyz/100)|
|ENKI_SCENARIO_ACTIVATE_CAPABILITY|![100%](https://progress-bar.xyz/100)|
|change_light_state|![100%](https://progress-bar.xyz/100)|
|check_light_state|![100%](https://progress-bar.xyz/100)|
|check_current_temperature|![100%](https://progress-bar.xyz/100)|
|check_current_humidity|![100%](https://progress-bar.xyz/100)|
|check_fan_speed|![100%](https://progress-bar.xyz/100)|
|check_fan_rotation_direction|![100%](https://progress-bar.xyz/100)|
|check_airflow_mode|![100%](https://progress-bar.xyz/100)|
|change_fan_speed|![100%](https://progress-bar.xyz/100)|
|change_fan_rotation_direction|![100%](https://progress-bar.xyz/100)|
|change_airflow_mode|![100%](https://progress-bar.xyz/100)|
|switch_electrical_power|![100%](https://progress-bar.xyz/100)|
|check_electrical_power|![100%](https://progress-bar.xyz/100)|
|check_battery_health|![100%](https://progress-bar.xyz/100)|
|check_motion_detection|![100%](https://progress-bar.xyz/100)|
|check_motion_detector_state|![100%](https://progress-bar.xyz/100)|
|check_contact_sensor_state|![100%](https://progress-bar.xyz/100)|
|check_vibration_detection|![100%](https://progress-bar.xyz/100)|
|check_vibration_detection_activation|![100%](https://progress-bar.xyz/100)|
|activate_vibration_detection|![100%](https://progress-bar.xyz/100)|
|check_contact_detection_activation|![100%](https://progress-bar.xyz/100)|
|activate_contact_detection|![100%](https://progress-bar.xyz/100)|
|check_vibration_sensibility_level|![100%](https://progress-bar.xyz/100)|
|change_vibration_sensibility_level|![100%](https://progress-bar.xyz/100)|
|check_siren_global_state|![100%](https://progress-bar.xyz/100)|
|switch_siren_status|![100%](https://progress-bar.xyz/100)|
|check_water_sensor_state|![100%](https://progress-bar.xyz/100)|
<!-- end -->

</details>

## Connect your Enki account

Reference your username and your password to connect to your Enki's account.

You can specifiy a refresh rate.

## Dev

### Live API test

This repository includes a standalone live diagnostics script that can authenticate against Enki
and print available devices/actions from your account. This can help to develop and debug the
component against the real API.

Before running it locally, install runtime dependencies:

```bash
python -m pip install aiohttp prettytable
```

Run the script with credentials as parameters:

```bash
python tools/enki_api_live.py --user "your-email@example.com" --password "your-password"
```

You can also use environment variables:

```bash
export ENKI_USER="your-email@example.com"
export ENKI_PASSWORD="your-password"
python tools/enki_api_live.py
```

Expected output

```bash
Fetching all devices...

Devices found: 15
+----+-----------------------+------------------------------+-----------+---------+--------+-----------------------+---------------+
| #  |          Name         |         Device type          | Device ID | Node ID | Status | Expected coverage (%) |   Protocols   |
+----+-----------------------+------------------------------+-----------+---------+--------+-----------------------+---------------+
| 1  |  Détecteur mouvements |           sensors            |    ...    |   ...   | Known  |          100          |     zigbee    |
| 2  |  Télécommande alarme  | remote_controls_and_switches |    ...    |   ...   | Known  |           0           |     zigbee    |
| 3  |       Ampoule 1       |            lights            |    ...    |   ...   |  NEW!  |           44          |     zigbee    |
| 4  |        Prise 2        |           outlets            |    ...    |   ...   | Known  |           28          |     zigbee    |
| 5  |         Caméra        |           cameras            |    ...    |   ...   | Known  |           0           | lexman_camera |
| .. |          ....         |             ...              |    ...    |   ...   |  ...   |          ...          |      ...      |
| 14 |   Thermomètre rouge   |           sensors            |    ...    |   ...   | Known  |          100          |     zigbee    |
| 15 |  Détecteur ouverture  |           sensors            |    ...    |   ...   | Known  |           90          |     zigbee    |
+----+-----------------------+------------------------------+-----------+---------+--------+-----------------------+---------------+

You have devices that haven't been listed or tested in this library yet.
Please submit a documentation PR to add them; you can add their names and include an image by editing the corresponding JSON files in the folder doc/devices

 - #3 > 5d7df749f8bb0659f50d263d (Ampoule 1)
```

---

> [!NOTE]
> This repository is based on the excellent [CyrilP/hass-enki-component](https://github.com/CyrilP/hass-enki-component) repository, which did not appear to be maintained in a consistent and sustainable manner.
