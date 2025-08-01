# Home Assistant Daikin Madoka

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

This is a custom component developed to support Daikin Madoka BRC1H thermostats in Home Assistant. 

This custom component has been evolved to become part of the Home Assistant core integrations and is awaiting to be integrated.

![](images/madoka.png)

![](images/integration.png)  ![](images/climate.png) ![](images/entities.png) 

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add `https://github.com/atanarro/daikin_madoka` as repository
   - Select "Integration" as category
   - Click "Add"
3. Install the integration through HACS
4. Restart Home Assistant

### Manual Installation

Download folder and copy under "custom_components" folder in the Home Assistant configuration folder.

## Requirements

Due to the thermostat security constraints, is has to be manually paired with the system where HomeAssistant runs. This has only been tested in Linux, but the following steps should be easy to follow:

1. Disconnect the thermostat from any other device (thermostat Bluetooth menu, forget). This has to be done to make the device visible during the scanning.
2. On a terminal, run "bluetoothctl"
3. Type "agent KeyboardDisplay"
4. Type "remove <BRC1H_MAC_ADDRESS>". This step helps to remove unsucessful previous pairings and makes the device visible.
5. Type "scan on" and wait until the mac is listed.
6. Type "scan off"
7. Type "pair <BRC1H_MAC_ADDRESS>". You will be presented a confirmation prompt, accept it.
8. Go to the thermostat and accept the pairing code. It requires to do it fairly soon after the previous step or it will be cancelled.
9. The device is ready and you can start the integration in Home Assistant.

A dedicated Bluetooth adapter is desirable. If you run Home Assistant in a virtual machine, it makes it easiser for the device to be used. In VMWare, make sure to remove the checkbox "Share bluetooth devices with guests". This way, the adapter will become visible to the virtual machine and will use it without problem. 

## Usage

A new integration will be available under the name "Daikin Madoka". You have to provide the following details:

- Bluetooth MAC Address of the BRC1H device(s)
- Name of the Bluetooth adapter (usually hci0)

The integration will scan for the devices and will create the thermostat and the temperature sensor.

## Troubleshooting

* **The integration form shows an error "The device could not be found" next to the adapter field but "hcitool dev" lists the device" **

This could be a problem related to the configuration of the DBUS service. Make sure DBUS is installed in the host (it generally is) and that it is available to your homeassistant docker.

You can test it using *bleak* CLI tool *bleak-lescan* inside your instance. Follow these steps:

```
$ docker exec -ti <homeassistant_container_id> /bin/bash
$ bleak-lescan -i <adapter>
```

If the following error appears, DBUS is not available to the docker instance.
```
File "/usr/local/lib/python3.8/site-packages/bleak/backends/bluezdbus/scanner.py", line 90, in start
    self._bus = await client.connect(self._reactor, "system").asFuture(loop)
twisted.internet.error.ConnectError: An error occurred while connecting: Failed to connect to any bus address. Last error: An error occurred while connecting: 2: No such file or directory..
"Failed to connect to any bus address"
```
To make DBus available you have to link /var/run/dbus/system_bus_socket inside the container and also run docker in privileged mode. 

Modify your docker-compose.yml:
```
volumes:
  - /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket
privileged: true
```

Kudos to [Jose](https://community.home-assistant.io/u/jcsogo) for the solution.

* **"Module pymadoka.connection is logging too frequently" warning in Home Assistant logs**

If you see warnings like "Module pymadoka.connection is logging too frequently. 200 messages since last count", this indicates that the underlying pymadoka library is generating excessive connection-related log messages. This typically happens due to:

- Bluetooth connectivity issues between Home Assistant and the thermostat
- Frequent connection/disconnection cycles
- Network interference or distance issues

To reduce log verbosity, add the following to your Home Assistant `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    pymadoka.connection: error
    pymadoka: warning
```

This will suppress debug and info level messages from the pymadoka library while still showing important warnings and errors. You can also set the level to `critical` if you want to suppress all but the most critical messages.

If the excessive logging persists, consider:
1. Checking the Bluetooth connection quality between Home Assistant and the thermostat
2. Ensuring the thermostat is within proper range of the Bluetooth adapter
3. Verifying that no other devices are interfering with the Bluetooth connection
4. Restarting the integration or Home Assistant if connection issues persist

* **BluZ "Operation already in progress" and "br-connection-canceled" errors**

If you see repeated error patterns like:
```
[org.bluez.Error.Failed] Operation already in progress
[org.bluez.Error.Failed] br-connection-canceled
```

This indicates a Bluetooth stack issue where connection attempts are overlapping and causing conflicts. To resolve this:

1. **Restart the Bluetooth service:**
   ```bash
   sudo systemctl restart bluetooth
   ```

2. **Reset the Bluetooth adapter:**
   ```bash
   sudo hciconfig hci0 down
   sudo hciconfig hci0 up
   ```

3. **Clear the Bluetooth cache and re-pair the device:**
   ```bash
   # Remove the existing pairing
   bluetoothctl
   remove <BRC1H_MAC_ADDRESS>
   exit
   
   # Restart Home Assistant and re-add the integration
   ```

4. **If using Docker, ensure proper Bluetooth access:**
   - Add `--privileged` flag to your Docker command
   - Or use specific device mapping: `--device=/dev/bus/usb`
   - Ensure DBus socket is mounted: `-v /var/run/dbus:/var/run/dbus:ro`

5. **Temporary workaround - Reduce logging level:**
   ```yaml
   logger:
     default: info
     logs:
       pymadoka.connection: critical
   ```

6. **Check for conflicting Bluetooth processes:**
   ```bash
   sudo lsof /dev/tty* | grep Blue
   ps aux | grep blue
   ```

If the issue persists, try:
- Using a dedicated Bluetooth adapter for Home Assistant
- Increasing the controller timeout in the integration configuration
- Restarting Home Assistant after making Bluetooth changes

**Recommended logging configuration for Bluetooth issues:**

Add this to your `configuration.yaml` to manage excessive Bluetooth logging:

```yaml
logger:
  default: info
  logs:
    # Reduce pymadoka connection logging
    pymadoka.connection: critical
    pymadoka: warning
    
    # Reduce Home Assistant Daikin Madoka integration logging for known Bluetooth issues
    custom_components.daikin_madoka: info
    
    # Optional: Reduce general Bluetooth logging
    homeassistant.components.bluetooth: warning
```

This configuration will:
- Set pymadoka connection logging to critical only (suppresses the repetitive BluZ errors)
- Keep integration logging at info level for important status updates  
- Reduce general Bluetooth component logging if needed

## TODO
This document.
Icon and integration images.

---

[releases-shield]: https://img.shields.io/github/release/atanarro/daikin_madoka.svg?style=for-the-badge
[releases]: https://github.com/atanarro/daikin_madoka/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/atanarro/daikin_madoka.svg?style=for-the-badge
[commits]: https://github.com/atanarro/daikin_madoka/commits/main
[license-shield]: https://img.shields.io/github/license/atanarro/daikin_madoka.svg?style=for-the-badge
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
