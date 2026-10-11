# Dreame Mower

[![Release](https://img.shields.io/github/v/release/keysim86/ha-dreame-mower?style=flat-square&label=release)](https://github.com/keysim86/ha-dreame-mower/releases)
[![Downloads](https://img.shields.io/github/downloads/keysim86/ha-dreame-mower/total?style=flat-square&label=downloads&color=orange)](https://github.com/keysim86/ha-dreame-mower/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange?style=flat-square)](https://hacs.xyz/)

> ⚠️ **Scope of support**
>
> I only own a **Dreame A1 Pro**, so that's the only model I can actively test and support. The integration is reported working on other Dreame mowers by the community (see the [compatibility table](#compatibility) below), but I can't fix model-specific issues for hardware I don't have.
>
> **MOVA mowers are not supported** — the login flow uses a different regional setup and I have no device to validate against. PRs are welcome if you want to add MOVA support.

**Control your Dreame A1 Pro robotic lawn mower directly from Home Assistant.**

Start, stop, and dock your mower, monitor battery and charging status, and more — all from your HA dashboard.

## What you get

| Entity | Type | What it does |
|--------|------|--------------|
| A1 Pro | Lawn Mower | Start, stop, return to dock |
| Map | Camera | Mowing zone map with named zones and no-go areas |
| Battery Level | Sensor | Current battery percentage |
| State | Sensor | What the mower is doing (mowing, charging, idle, error) |
| Charging Status | Sensor | Charging or not |
| Firmware Version | Sensor | Installed firmware |
| Cleaning Count | Sensor | Total number of mowing sessions |
| Total Cleaning Time | Sensor | Cumulative mowing time (minutes) |
| Total Cleaned Area | Sensor | Cumulative mowed area (m²) |
| First Cleaning Date | Sensor | Date of the very first mow |
| Total Runtime | Sensor | Total device runtime (minutes) |
| Has Saved Map | Binary Sensor | Whether the mower has a saved map |
| Scheduled Clean | Binary Sensor | Whether a scheduled mowing is active |
| Do Not Disturb | Switch | Enable/disable DnD mode |
| Stop Mowing | Button | Stop current mowing task and return to dock |
| Mow &lt;zone&gt; | Button | Start mowing a single zone (one button per zone; available while the mower is in the station or idle) |
| Error notification | Persistent notification | Automatic alert when the mower reports an error (translated in FR/EN) |

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots menu > **Custom repositories**
3. Add `keysim86/ha-dreame-mower` as **Integration**
4. Search for and install **Dreame Mower**
5. Restart Home Assistant
6. Go to **Settings** > **Integrations** > **Add Integration** > **Dreame Mower**
7. Restart and configure the integration

### Manual

Copy the `custom_components/dreame_mower` folder to your Home Assistant `custom_components/` directory and restart.

## Configuration

Use the same Dreame / Xiaomi account credentials as the Dreamehome app.

## Compatibility

| Model | Status | Notes |
|-------|--------|-------|
| Dreame A1 Pro (`dreame.mower.g2422`) | Officially supported | Tested by me on every release |
| Dreame A1 (`dreame.mower.p2255`) | Community | Reported working |
| Dreame A2 (`dreame.mower.g2408`) | Community | Reported working |
| Dreame A2 1200 (`dreame.mower.g2568a`) | Community | Reported working |
| Dreame A3 | Community | Reported working |
| MOVA (any model) | Not supported | Login flow differs, I have no device to test |

**"Officially supported"** means I test it on every release and fix issues you report. **"Community"** means other users have got it working but I can't debug model-specific issues without the hardware — PRs welcome.

If you try it on a different Dreame model, please [open an issue](https://github.com/keysim86/ha-dreame-mower/issues) to let me know how it goes!

## Credits

This integration is a fork of [dreame-mower-a1-pro](https://github.com/nicolasglg/dreame-mower-a1-pro) by [@nicolasglg](https://github.com/nicolasglg), itself based on [dreame-mower](https://github.com/bhuebschen/dreame-mower) by [@bhuebschen](https://github.com/bhuebschen) and [dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) by [@Tasshack](https://github.com/Tasshack).
