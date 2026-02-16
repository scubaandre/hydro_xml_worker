# Hydro Ottawa xml scaper app (add-on)

[![GitHub Release](https://img.shields.io/github/release/rhounsell/home-assistant-green-button.svg?style=for-the-badge)](https://github.com/rhounsell/home-assistant-green-button/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/rhounsell/home-assistant-green-button?style=for-the-badge)](https://github.com/rhounsell/home-assistant-green-button/commits)
[![License][license-shield]](LICENSE)

A complete solution to automate the extraction of electricity usage and cost data from the Hydro Ottawa portal (`hydroottawa.savagedata.com`) directly into the Home Assistant Energy Dashboard.

## ⚡ Overview
This repository provides a Home Assistant Add-on that works in tandem with the **Green Button** standard. It eliminates the need for manual downloads by running a "headless" background scraper that simulates a login, intercepts the data stream, and provides it to Home Assistant in real-time.

### The Stack:
* **The Scraper (Add-on):** A persistent service that logs in and exports Green Button XML data.
* **Browserless:** The Chromium engine that powers the headless navigation.
* **Folder Watcher:** Monitors for new data files instantly.
* **Green Button Integration:** Processes the XML files into Energy Dashboard sensors.

---

## 🚀 Quick Start
1. **Install Prerequisites:** You will need the **Browserless** add-on and the **Green Button** HACS integration.
2. **Configure Folder Watcher:** Add the `/share/hydro_ottawa` path to your `configuration.yaml`.
3. **Install the Add-on:** Located in the `hydro_xml_worker` directory of this repo.
4. **Automate the Import:** Use the provided event-based automation to trigger imports whenever the scraper finishes its run.

> **Note:** Detailed installation steps, automation YAML, and configuration schemas can be found inside the [hydro_xml_worker](./hydro_xml_worker/README.md) folder.

---

## 🛠 Troubleshooting
* Check the add-on logs for updates.
* Enable **Debug Mode** to see screenshots of the portal login process in your `/share` folder.
* Note: Hydro Ottawa typically has a 24-48 hour delay on data availability.

---

*Designed, supervised by humans. Created by AI.* 🤖🤝👤
