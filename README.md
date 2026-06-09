# Enki integration for Home Assistant (Unofficial)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/StephaneBranly/ha-enki?color=41BDF5&style=for-the-badge)](https://github.com/StephaneBranly/ha-enki/releases/latest)

The unofficial Enki intregration for Home Assistant.

<img src="https://raw.githubusercontent.com/StephaneBranly/ha-enki/main/src/icon.png">

> [!NOTE]
> This repository is based on the excellent [CyrilP/hass-enki-component](https://github.com/CyrilP/hass-enki-component) repository, which did not appear to be maintained in a consistent and sustainable manner.

> [!NOTE]
> This custom component is relatively new. It does not include all Enki components and may contain bugs.

## Tested devices:

- Eglo V-link tunable white
- Inspire Cadix ceiling fan with light
- Lexman RGBW Light

## Live API test

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
