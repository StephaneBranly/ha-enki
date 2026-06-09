# Enki integration for Home Assistant (Unofficial)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/StephaneBranly/ha-enki?color=41BDF5&style=for-the-badge)](https://github.com/StephaneBranly/ha-enki/releases/latest)

The unofficial Enki intregration for Home Assistant.

<img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/main/src/icon.png">

> [!NOTE]
> This custom component is relatively new. It does not include all Enki components and may contain bugs.

## Known devices:

<!-- start devices -->
| Name | Image | Id | Coverage (%) | Tested |
|---|---|---|---|---|
|na<br/>Lexman||*5f1192bc23b5dec92ac93eb4*|![10%](https://progress-bar.xyz/10)|❌|
|na<br/>Lexman||*5e8bad4e8eff8efc7c83ba49*|![16%](https://progress-bar.xyz/16)|❌|
|na<br/>Sedea||*6633842c9f53b36a99838c94*|![33%](https://progress-bar.xyz/33)|❌|
|na<br/>Lexman||*5e26cc33777472061d55e340*|![33%](https://progress-bar.xyz/33)|❌|
|na<br/>Lexman||*5f16c4aca80024b5af0561a1*|![16%](https://progress-bar.xyz/16)|❌|
|RGB E27 Light<br/>Lexman|<img src='./doc/devices/5d7df749f8bb0659f50d263d.webp'  width='100'/>|*5d7df749f8bb0659f50d263d*|![66%](https://progress-bar.xyz/66)|✅|
<!-- end -->

<!-- - Eglo V-link tunable white
- Inspire Cadix ceiling fan with light
- Lexman RGBW Light -->

## Supported capabilities

Different device capabilities are curently being integrated to this custom component.

<details>

<summary>Capabilities coverage</summary>

<!-- start capabilities -->
| Capability | Coverage (%) |
|---|---|
|change_brightness|![100%](https://progress-bar.xyz/100)|
|change_color_temperature|![100%](https://progress-bar.xyz/100)|
|change_hue|![100%](https://progress-bar.xyz/100)|
|change_light_state|![100%](https://progress-bar.xyz/100)|
|change_saturation|![100%](https://progress-bar.xyz/100)|
|check_battery_health|![100%](https://progress-bar.xyz/100)|
|check_light_state|![100%](https://progress-bar.xyz/100)|
|check_lighting_remote_state|![100%](https://progress-bar.xyz/100)|
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
python -m pip install aiohttp
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

> [!NOTE]
> This repository is based on the excellent [CyrilP/hass-enki-component](https://github.com/CyrilP/hass-enki-component) repository, which did not appear to be maintained in a consistent and sustainable manner.
