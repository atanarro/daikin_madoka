## Daikin Madoka Integration

This integration provides support for Daikin Madoka BRC1H thermostats in Home Assistant.

### Features

- **Climate Control**: Full thermostat control with temperature setting, mode changes, and fan control
- **Temperature Sensors**: Monitor inside and outside temperature readings
- **Local Communication**: Uses Bluetooth for local communication with the thermostat
- **Config Flow**: Easy setup through the Home Assistant UI

### Requirements

- Daikin Madoka BRC1H thermostat
- Bluetooth adapter on your Home Assistant system
- Manual Bluetooth pairing (see documentation for detailed steps)

### Supported Entities

- **Climate**: Main thermostat control
- **Sensor**: Inside temperature sensor
- **Sensor**: Outside temperature sensor (if available)

### Installation Notes

Due to security constraints of the thermostat, manual Bluetooth pairing is required before setting up the integration. Please refer to the full documentation for detailed pairing instructions.

The integration requires the `pymadoka` Python library which will be automatically installed. 