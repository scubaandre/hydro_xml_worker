# Hydro Ottawa Scraper

Automate the extraction of electricity usage and cost data from the Hydro Ottawa portal into your Home Assistant Energy Dashboard.

## How it Works
1.  **The Scraper (This Add-on):** Runs as a persistent background service. It logs into the Hydro Ottawa portal using a "headless" browser, selects both **Usage** and **Billing** data, intercepts the Green Button XML stream, and saves it to your `/share/hydro_ottawa` folder.
2.  **Browserless:** A required companion add-on that provides the Chromium engine for the scraper.
3.  **Green Button Integration:** A custom integration that reads the saved XML file and pushes it into the Home Assistant Energy Dashboard.
4.  **Folder Watcher:** A native Home Assistant component that monitors the `/share` folder and triggers an import the moment new data is saved.

---

## Installation & Setup

### 1. Prerequisites
* **Browserless:** Install the [Browserless](https://github.com/alexbelgium/hassio-addons/tree/master/browserless_chrome) add-on from the Home Assistant Community Store.
* **Green Button Integration:** Install the [Green Button Integration](https://github.com/rhounsell/home-assistant-green-button) via HACS.
* **Folder Watcher:** Add the following to your `configuration.yaml` and **restart Home Assistant**:
    ```yaml
    folder_watcher:
      - folder: /share/hydro_ottawa
        patterns:
          - 'hydro_data.xml'
    ```

### 2. Add-on Configuration
Install this add-on and configure the following:
* **Username/Password:** Your Hydro Ottawa portal credentials.
* **Browserless URL:** Usually `ws://homeassistant:3000`.
* **Scrapes per day:** How often the background service should refresh data (e.g., `4` for every 6 hours).
* **Debug Mode:** Enable this to save screenshots to `/share/hydro_ottawa` if you encounter login issues.

---

## Automation: The "Importer"
Because the add-on manages its own schedule, you only need an automation to "watch" for the file and import it. 

### Event-Based Import (Recommended)
This automation triggers the millisecond the scraper finishes writing the file.

```yaml
alias: "Hydro Ottawa: Import XML on Update"
description: "Automatically imports data whenever the scraper finishes a new file"
trigger:
  - platform: event
    event_type: folder_watcher
    event_data:
      event_type: closed
      file: hydro_data.xml
action:
  - action: green_button.import_espi_xml
    data:
      xml_file_path: /share/hydro_ottawa/hydro_data.xml
mode: single