# Enki integration for Home Assistant (Unofficial)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=StephaneBranly&repository=ha-enki&category=integration"><img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/refs/heads/main/doc/illustrations/header.png" alt="Enki integration logo" width="100%"></a>

<p align="center">
  <a href="https://github.com/hacs/integration"><img alt="Home Assistant" src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge"></a>
  <a href="https://github.com/StephaneBranly/ha-enki/releases/latest"><img alt="Last release" src="https://img.shields.io/github/v/release/StephaneBranly/ha-enki?color=41BDF5&style=for-the-badge"></a>
</p>
<p align="center">
 <a href="https://github.com/stephanebranly/ha-enki/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/stephanebranly/ha-enki?style=flat-square" /></a>
  <a href="https://github.com/stephanebranly/ha-enki/releases"><img alt="Downloads" src="https://img.shields.io/github/downloads/stephanebranly/ha-enki/total?style=flat-square&color=1f883d"></a>
</p>
<p align="center">
    <img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/main/src/icon.png" width="100px">
</p>
<p align="center">
    <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=StephaneBranly&repository=ha-enki&category=integration"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Download on HACS" /></a>
</p>

Home Assistant integration for the Enki (by Leroy Merlin) smart home ecosystem.
Control lights, fans, switches, covers, sensors, security devices, scenarios, and more

<p align="center">
  <a href='#installation'>📦 Installation</a> •
  <a href='#connect-your-enki-account'>⚙️ Connect your enki account</a> •
  <a href='#tested-devices'>📱 Tested Devices</a> •
  <a href='#supported-capabilities'>🔌 Supported capabilities</a> •
  <a href='#check-compatibility-in-30-seconds'>🧪 Check compatibility in 30 seconds</a> •
  <a href='#contributing'>❤️ Contributing</a>
</p>

<img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/refs/heads/main/doc/illustrations/devices.png" alt="Enki integration logo" width="100%">

## Tested devices:

> [!TIP]
> Don't see your device in the list of tested devices?
>
> It may still work perfectly. The devices listed above are only those that have been explicitly tested by contributors.
>
> Many Enki devices share the same capabilities and protocols, meaning support can often extend to devices that have never been tested before.
>
> If you successfully use an unlisted device, please consider opening an issue or submitting a pull request to help improve compatibility information for the community.

<!-- start devices -->

| Name                                            | Image                                                                 | Id                         | Coverage (%)                          | Tested |
| ----------------------------------------------- | --------------------------------------------------------------------- | -------------------------- | ------------------------------------- | ------ |
| RGB E27 Light<br/>Lexman                        | <img src='./doc/devices/5d7df749f8bb0659f50d263d.webp'  width='100'/> | _5d7df749f8bb0659f50d263d_ | ![44%](https://progress-bar.xyz/44)   | ✅     |
| Water leak detector<br/>Lexman                  | <img src='./doc/devices/651eada55b3a798ef6b6bc5c.jpg'  width='100'/>  | _651eada55b3a798ef6b6bc5c_ | ![100%](https://progress-bar.xyz/100) | ❌     |
| ON/OFF relay<br/>Equation                       | <img src='./doc/devices/63a053851a423d4a245a877c.png'  width='100'/>  | _63a053851a423d4a245a877c_ | ![28%](https://progress-bar.xyz/28)   | ❌     |
| Contact detector<br/>Lexman                     | <img src='./doc/devices/5f1192bc23b5dec92ac93eb4.jpg'  width='100'/>  | _5f1192bc23b5dec92ac93eb4_ | ![90%](https://progress-bar.xyz/90)   | ✅     |
| Outlet 16A, 3680A<br/>Lexman                    | <img src='./doc/devices/5e258991b472bf9d87b8483f.webp'  width='100'/> | _5e258991b472bf9d87b8483f_ | ![28%](https://progress-bar.xyz/28)   | ✅     |
| Siren<br/>Lexman                                | <img src='./doc/devices/5f16c4aca80024b5af0561a1.jpg'  width='100'/>  | _5f16c4aca80024b5af0561a1_ | ![50%](https://progress-bar.xyz/50)   | ❌     |
| Thermometer with display<br/>Sonoff             | <img src='./doc/devices/6634999c9f53b36a99838c95.jpg'  width='100'/>  | _6634999c9f53b36a99838c95_ | ![100%](https://progress-bar.xyz/100) | ❌     |
| Connected thermometer<br/>Sedea                 | <img src='./doc/devices/6633842c9f53b36a99838c94.webp'  width='100'/> | _6633842c9f53b36a99838c94_ | ![100%](https://progress-bar.xyz/100) | ✅     |
| Cadix ceiling fan with light<br/>Inspire        | <img src='./doc/devices/6827098c5f52437f08d9d7a1.jpg'  width='100'/>  | _6827098c5f52437f08d9d7a1_ | ![55%](https://progress-bar.xyz/55)   | ✅     |
| Radiator<br/>Noirot                             | <img src='./doc/devices/67a4b12bae1eca4709a45680.jpg'  width='100'/>  | _67a4b12bae1eca4709a45680_ | ![9%](https://progress-bar.xyz/9)     | ❌     |
| Motion detector<br/>Lexman                      | <img src='./doc/devices/5e26cc33777472061d55e340.jpg'  width='100'/>  | _5e26cc33777472061d55e340_ | ![100%](https://progress-bar.xyz/100) | ✅     |
| Lexman In-Wall Roller Shutter Module<br/>Lexman | <img src='./doc/devices/photo.png'  width='100'/>                     | _622ad2122eab0cd7e5890eeb_ | ![66%](https://progress-bar.xyz/66)   | ✅     |

<!-- end -->

<img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/refs/heads/main/doc/illustrations/scenarios.png" alt="Enki integration logo" width="100%">

In addition to physical devices, integration allows you to retrieve your scenarios and activate them using push buttons!

<img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/refs/heads/main/doc/illustrations/security.png" alt="Enki integration logo" width="100%">

You can also access your Enki home security system—right from Home Assistant!

## Supported capabilities

Different device capabilities are curently being integrated to this custom component.

<details>

<summary>Capabilities coverage</summary>

<!-- start capabilities -->

| Capability                           | Coverage (%)                          |
| ------------------------------------ | ------------------------------------- |
| ENKI_HOMES_LIST                      | ![100%](https://progress-bar.xyz/100) |
| ENKI_BFF_ITEMS                       | ![100%](https://progress-bar.xyz/100) |
| ENKI_NODE_CAPABILITY                 | ![100%](https://progress-bar.xyz/100) |
| ENKI_SCENARIO_LIST_CAPABILITY        | ![100%](https://progress-bar.xyz/100) |
| ENKI_SCENARIO_ACTIVATE_CAPABILITY    | ![100%](https://progress-bar.xyz/100) |
| change_light_state                   | ![100%](https://progress-bar.xyz/100) |
| check_light_state                    | ![100%](https://progress-bar.xyz/100) |
| check_current_temperature            | ![100%](https://progress-bar.xyz/100) |
| check_current_humidity               | ![100%](https://progress-bar.xyz/100) |
| check_fan_speed                      | ![100%](https://progress-bar.xyz/100) |
| check_fan_rotation_direction         | ![100%](https://progress-bar.xyz/100) |
| check_airflow_mode                   | ![100%](https://progress-bar.xyz/100) |
| change_fan_speed                     | ![100%](https://progress-bar.xyz/100) |
| change_fan_rotation_direction        | ![100%](https://progress-bar.xyz/100) |
| change_airflow_mode                  | ![100%](https://progress-bar.xyz/100) |
| switch_electrical_power              | ![100%](https://progress-bar.xyz/100) |
| check_electrical_power               | ![100%](https://progress-bar.xyz/100) |
| check_battery_health                 | ![100%](https://progress-bar.xyz/100) |
| check_motion_detection               | ![100%](https://progress-bar.xyz/100) |
| check_motion_detector_state          | ![100%](https://progress-bar.xyz/100) |
| check_contact_sensor_state           | ![100%](https://progress-bar.xyz/100) |
| check_vibration_detection            | ![100%](https://progress-bar.xyz/100) |
| check_vibration_detection_activation | ![100%](https://progress-bar.xyz/100) |
| activate_vibration_detection         | ![100%](https://progress-bar.xyz/100) |
| check_contact_detection_activation   | ![100%](https://progress-bar.xyz/100) |
| activate_contact_detection           | ![100%](https://progress-bar.xyz/100) |
| check_vibration_sensibility_level    | ![100%](https://progress-bar.xyz/100) |
| change_vibration_sensibility_level   | ![100%](https://progress-bar.xyz/100) |
| check_siren_global_state             | ![100%](https://progress-bar.xyz/100) |
| switch_siren_status                  | ![100%](https://progress-bar.xyz/100) |
| check_roller_shutter_state           | ![100%](https://progress-bar.xyz/100) |
| change_shutter_position              | ![100%](https://progress-bar.xyz/100) |
| stop_change_shutter_position         | ![100%](https://progress-bar.xyz/100) |
| change_roller_shutter_mode           | ![100%](https://progress-bar.xyz/100) |
| check_water_sensor_state             | ![100%](https://progress-bar.xyz/100) |

<!-- end -->

</details>

## Installation

### Using HACS

1. Open HACS
2. Click "Custom repositories"
3. Add:

https://github.com/StephaneBranly/ha-enki

Category: Integration

4. Install the integration
5. Restart Home Assistant

### Configuration

Settings → Devices & Services → Add Integration → Enki

## Connect your Enki account

Reference your username and your password to connect to your Enki's account.

You can specifiy a refresh interval.

## Check compatibility in 30 seconds

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

## Contributing

This project is developed in my spare time and community contributions are always welcome.

Whether you want to improve the code, test new devices, report issues, improve translations, write documentation, or simply share feedback, your help is valuable.

No contribution is too small. Every bug report, device test, documentation fix, or pull request helps improve Enki support for everyone.

If you own an Enki-compatible device that is not yet listed, please consider running the diagnostic tool and opening an issue or submitting a pull request.
Let's build the best Enki integration for Home Assistant together

> [!NOTE]
> This repository is based on the excellent [CyrilP/hass-enki-component](https://github.com/CyrilP/hass-enki-component) repository, which did not appear to be maintained in a consistent and sustainable manner.
