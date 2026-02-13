# Changelog

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
