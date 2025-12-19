# Hydro-Québec – Consommation d’énergie
# WORK IN PROGRESS --- ONGOING TEST

![hacs_badge](https://img.shields.io/badge/HACS-Cntegration retrieves energy consumption and peak event data from Hydro-Québec's open data API.

## Features
- Displays latest consumption in kWh.
- Shows peak event status.
- Updates every hour (configurable).

## Installation
1. Add this repository to HACS as a custom integration.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration → Hydro-Québec**.

## Configuration
No credentials required. Data is fetched from Hydro-Québec's public API.

## Sensors
- `sensor.hydro_quebec_last_consumption` – Latest consumption in kWh.
- `sensor.hydro_quebec_peak_event` – Peak event status.

## Links
