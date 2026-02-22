# Changelog

## [0.1.6] - 2026-02-21

### Added
- **Historical Export:** Added `days_to_export` configuration option. Users can now specify how many days of history to pull (configurable between 2 and 90 days).
- **Date Picker Automation:** The scraper now automatically calculates and injects the start date into the Hydro Ottawa portal using JavaScript event bubbling to ensure the Blazor framework registers the change.

### Fixed
- **Syntax Error:** Resolved an "unmatched bracket" error in the JavaScript evaluation block that was causing a `SyntaxError` on startup.
- **Versioning Standard:** Transitioned from `00.01.05` to standard Semantic Versioning `0.1.6` for better compatibility with automation tools.
- **Loop Reliability:** Fixed a variable reference error (`i` vs `_`) in the download wait-loop and improved the main loop's crash recovery logic.

### Changed
- **Config UI:** Enhanced the configuration page with detailed descriptions for each variable to improve the user onboarding experience.
- **Logging:** Optimized logging levels; technical connection details moved to `DEBUG`, while milestones remain in `INFO`.

## [00.01.05] - 2026-02-16
### Added
- better configuration field description in EN and FR

## [00.01.04] - 2026-02-15
### Fixed
- debug logging fixed 

## [00.01.03] - 2026-02-13
### Added
- **Milestone Debugging:** Detailed log output for every stage of the scraping process (Login, Navigation, Interception).
- **CPU Safety Valve:** Implemented `asyncio.sleep` in the main loop and error handlers to prevent high CPU usage (busy-looping).
- **Live Config Reload:** The service now re-reads `scrapes_per_day` and `debug_mode` at the start of every cycle without needing a restart.

### Fixed
- Resolved an issue where the add-on would consume 25% CPU when idling or failing.
- Fixed a timing bug where the scrape would attempt to start before Browserless was fully ready.

### Changed
- Refined the "Green Button" download logic to ensure both Usage and Billing checkboxes are reliably toggled.

## [00.01.02] - 2026-02-12
### Changed
- Converted add-on to a persistent background service.
- Implemented internal scheduling based on `scrapes_per_day`.
- Added `PYTHONUNBUFFERED` for real-time log streaming.
- Improved logic for "Billing/Cost" checkbox selection.

## [00.01.01] - 2026-02-07
### Added
- Support for including Billing/Cost data in the XML export.
- Precise element targeting using Radzen input IDs.

## [00.01.00] - 2026-02-06
### Added
- **Debug Mode**: New configuration toggle to save step-by-step screenshots to `/share/hydro_ottawa/` for easier troubleshooting.
- **Blazor Event Dispatching**: Enhanced credential injection to ensure compatibility with Hydro Ottawa's dynamic portal.
- **Network Wiretap**: Implemented CDP (Chrome DevTools Protocol) interception to capture the XML data stream directly from the API.
- **Version Tracking**: Formalized versioning string inside the Python logs and Docker labels.

### Changed
- Refactored login logic to handle redirect delays more gracefully.
- Updated documentation and README with setup instructions for Browserless and Green Button integrations.

### Fixed
- Resolved an issue where the download button was clicked before the Blazor state was fully ready.
- Fixed a bug where the `hydro_data.xml` file could be locked if the script crashed mid-write.
## 0.00.08
- Added randomized jitter (0-45s) to prevent synchronized scraping.
- Added stealth headers to mimic a real Chrome browser.
- New configuration option: `scrapes_per_day` (1-24).
- Added automatic cleanup of old debug screenshots in `/share`.
- Optimized Blazor-safe login injection.

## 0.00.07
- Standardized `config.yaml` schema for Home Assistant Supervisor compatibility.
- Fixed `login_timeout` and `browser_url` regex validation.

## 0.00.01 - 0.00.06
- Initial local development and proof-of-concept.

- Implemented Browserless CDP session for XML interception.
