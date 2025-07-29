# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - Current

### Fixed
- Fixed "Bootstrap stage 2 timeout" error by increasing controller startup timeout from 10 to 60 seconds
- Added better timeout error logging for debugging connection issues

### Added
- New configurable controller_timeout option in configuration flow (default: 60 seconds)
- Controller timeout configuration in config flow with translation support

### Changed
- Improved error handling for controller connection timeouts
- Updated Spanish and English translations for new timeout configuration

## [1.0.1] - 2025-01-15

### Added
- HACS compatibility
- GitHub workflows for validation and releases
- Improved documentation with installation instructions
- Info.md for HACS integration display

### Changed
- Updated manifest.json with proper documentation and issue tracker URLs
- Enhanced README with HACS installation instructions and badges

### Fixed
- Various improvements for HACS compliance

## [1.0.0] - Initial Release

### Added
- Initial release of Daikin Madoka integration
- Support for BRC1H thermostats
- Climate entity with full thermostat control
- Temperature sensors for inside and outside readings
- Bluetooth communication support
- Config flow for easy setup 