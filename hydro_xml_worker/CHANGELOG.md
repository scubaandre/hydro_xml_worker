# Changelog

## v0.1.9‑2

### Changed
- Replaced the numeric screenshot counter with label‑based screenshot filenames (`debug_<label>.png`) for clearer, human‑readable debugging.

## v0.1.9

### Added
- Per‑run debug screenshots (`debug_01.png`, `debug_02.png`, …) for clearer diagnostics.
- Global 300‑second scrape timeout to prevent hung browser sessions.

### Changed
- Rolled back to the stable 0.1.6 scraping logic for improved reliability.
- Error screenshots now follow the incremental naming system.

### Fixed
- Improved visibility into login, navigation, and export stages through additional screenshots.
- Ensured the main loop recovers cleanly after timeouts or unexpected failures.

## v0.1.8

### Added
- Asynchronous HTTP handling using `aiohttp`.
- Deterministic waits (`waitForSelector`, `waitForNavigation`, `waitForFunction`) replacing fixed delays.
- Hardened login flow using native typing and clicking.
- Global 300‑second scrape timeout.

### Changed
- Reworked request interception to avoid race conditions.
- Disabled interception automatically after the first successful XML capture.
- Improved error handling around browser closure and request continuation.
- Validated `scrapes_per_day` to prevent invalid configurations.

### Fixed
- Added per‑run screenshot counter for clean debugging.
- Added screenshots at key checkpoints (login, navigation, export, exceptions).
- Improved reliability of XML capture when multiple API calls fire.

## v0.1.6 — 2026‑02‑21

### Added
- `days_to_export` configuration option for historical exports.
- Automatic date injection into the Hydro Ottawa portal using Blazor‑safe event bubbling.

### Changed
- Adopted Semantic Versioning (`0.1.6`).
- Improved configuration UI descriptions.
- Adjusted logging levels for clearer output.

### Fixed
- Corrected a JavaScript syntax error in the evaluation block.
- Resolved a variable reference issue in the download wait loop.
- Improved main loop crash recovery.

## 00.01.05 — 2026‑02‑16

### Added
- Improved configuration field descriptions (EN/FR).

## 00.01.04 — 2026‑02‑15

### Fixed
- Debug logging output.

## 00.01.03 — 2026‑02‑13

### Added
- Detailed milestone logging for each scraping stage.
- CPU safety valve using `asyncio.sleep`.
- Live config reload for `scrapes_per_day` and `debug_mode`.

### Changed
- Refined Green Button download logic.

### Fixed
- Reduced idle CPU usage.
- Corrected timing issue when Browserless was not yet ready.

## 00.01.02 — 2026‑02‑12

### Changed
- Converted add‑on to a persistent background service.
- Implemented internal scheduling based on `scrapes_per_day`.
- Enabled real‑time log streaming with `PYTHONUNBUFFERED`.
- Improved Billing/Cost checkbox logic.

## 00.01.01 — 2026‑02‑07

### Added
- Billing/Cost data support.
- Precise Radzen input targeting.

## 00.01.00 — 2026‑02‑06

### Added
- Debug mode with step‑by‑step screenshots.
- Blazor‑safe credential injection.
- CDP interception for XML capture.
- Version tracking in logs and Docker labels.

### Changed
- Improved login handling for redirect delays.
- Updated documentation for Browserless and Green Button setup.

### Fixed
- Corrected timing around Blazor readiness.
- Resolved file‑locking issue during XML writes.

## 0.00.08

### Added
- Randomized jitter (0–45s) to avoid synchronized scraping.
- Stealth headers to mimic real Chrome.
- `scrapes_per_day` configuration (1–24).
- Automatic cleanup of old debug screenshots.
- Optimized Blazor‑safe login injection.

## 0.00.07

### Changed
- Standardized `config.yaml` schema.
- Improved validation for `login_timeout` and `browser_url`.

## 0.00.01–0.00.06

### Added
- Initial development and proof‑of‑concept.
- Browserless CDP session for XML interception.
