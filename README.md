# hydro_xml_worker

Automate the extraction of electricity usage data from the Hydro Ottawa portal hosted on hydroottawa.savagedata.com, into your Home Assistant Energy Dashboard.

## 🧩 How it Works
1. **The Scraper (This Add-on):** Logs into the Hydro Ottawa portal using a "headless" browser, intercepts the Green Button XML data, and saves it to your `/share` folder.
2. **Browserless:** A required companion add-on that provides the "engine" for the scraper.
3. **Green Button Integration:** A custom integration that reads the saved XML file and pushes it into the Energy Dashboard.

---

## 🚀 Installation & Setup

### 1. Prerequisites
* **Browserless:** Install the "Browserless" add-on from the Home Assistant Community Add-ons store. Ensure it is running.
* **Folder Watcher:** Add the following to your `configuration.yaml` to allow Home Assistant to "see" when the scraper finishes:
    ```yaml
    folder_watcher:
      - folder: /share/hydro_ottawa
        patterns:
          - 'hydro_data.xml'
    ```

### 2. Add-on Configuration
Install this add-on and fill in the following:
* **Username/Password:** Your Hydro Ottawa portal credentials.
* **Browserless URL:** Usually `ws://homeassistant:3000` or the IP of your HA instance.
* **Scrapes per day:** How often you want to check for new data (Hydro Ottawa usually updates once daily).

### 3. Energy Dashboard Integration
Install the [Green Button Integration] https://github.com/rhounsell/home-assistant-green-button (via HACS). This integration provides the service needed to process the XML file saved by this scraper.

---

## 🤖 Recommended Automation
To fully automate this, use a sequence that starts the scraper and waits for the file to be saved before importing:

```yaml
alias: "Hydro Ottawa: Daily Update"
trigger:
  - platform: time_pattern
    hours: "/6" # Adjust based on your 'Scrapes per day' setting
action:
  - action: hassio.addon_start
    data:
      addon: [YOUR_ADDON_SLUG]
  - wait_for_trigger:
      - platform: event
        event_type: folder_watcher
        event_data:
          event_type: closed
          file: hydro_data.xml
    timeout: "00:05:00"
  - action: green_button.import_espi_xml
    data:
      xml_file_path: /share/hydro_ottawa/hydro_data.xml
