"""Platform for the Daikin AC."""
import asyncio
from datetime import timedelta
import logging

from pymadoka import Controller, discover_devices, force_device_disconnect
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE,
    CONF_DEVICES,
    CONF_FORCE_UPDATE,
    CONF_SCAN_INTERVAL,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant

from . import config_flow  # noqa: F401
from .const import CONTROLLERS, DOMAIN, TIMEOUT, CONF_CONTROLLER_TIMEOUT

PARALLEL_UPDATES = 0
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

COMPONENT_TYPES = ["climate", "sensor"]

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    vol.All(
        cv.deprecated(DOMAIN),
        {
            DOMAIN: vol.Schema(
                {
                    vol.Required(CONF_DEVICES, default=[]): vol.All(
                        cv.ensure_list, [cv.string]
                    ),
                    vol.Optional(CONF_FORCE_UPDATE, default=True): bool,
                    vol.Optional(CONF_DEVICE, default="hci0"): cv.string,
                    vol.Optional(CONF_SCAN_INTERVAL, default=5): cv.positive_int,
                    vol.Optional(CONF_CONTROLLER_TIMEOUT, default=TIMEOUT): cv.positive_int,
                }
            )
        },
    ),
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the component."""

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Pass conf to all the components."""

    controllers = {}
    for device in entry.data[CONF_DEVICES]:
        if entry.data[CONF_FORCE_UPDATE]:
            await force_device_disconnect(device)
        controllers[device] = Controller(device, adapter=entry.data[CONF_DEVICE])

    await discover_devices(
        adapter=entry.data[CONF_DEVICE], timeout=entry.data[CONF_SCAN_INTERVAL]
    )

    # Get controller timeout from config, fallback to default if not set
    controller_timeout = entry.data.get(CONF_CONTROLLER_TIMEOUT, TIMEOUT)

    for device, controller in controllers.items():
        try:
            await asyncio.wait_for(controller.start(), timeout=controller_timeout)
        except ConnectionAbortedError as connection_aborted_error:
            _LOGGER.error(
                "Could not connect to device %s: %s",
                device,
                str(connection_aborted_error),
            )
        except asyncio.TimeoutError:
            _LOGGER.error(
                "Timeout connecting to device %s after %d seconds",
                device,
                controller_timeout,
            )
        except Exception as e:
            # Handle BluZ specific errors and other connection issues
            error_msg = str(e).lower()
            if "operation already in progress" in error_msg:
                _LOGGER.warning(
                    "Bluetooth operation conflict for device %s. "
                    "Try restarting the Bluetooth service or Home Assistant. Error: %s",
                    device,
                    str(e),
                )
            elif "br-connection-canceled" in error_msg:
                _LOGGER.warning(
                    "Bluetooth connection canceled for device %s. "
                    "Device may be out of range or Bluetooth stack issue. Error: %s",
                    device,
                    str(e),
                )
            elif "dbus" in error_msg:
                _LOGGER.error(
                    "DBus connection issue for device %s. "
                    "Ensure DBus is available to Home Assistant. Error: %s",
                    device,
                    str(e),
                )
            else:
                _LOGGER.error(
                    "Unexpected error connecting to device %s: %s",
                    device,
                    str(e),
                )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {CONTROLLERS: controllers}
    tasks = [
        hass.config_entries.async_forward_entry_setups(entry, [component])
        for component in COMPONENT_TYPES
    ]
    await asyncio.gather(*tasks)

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await asyncio.wait(
        [
            hass.async_create_task(hass.config_entries.async_forward_entry_unload(config_entry, component))
            for component in COMPONENT_TYPES
        ]
    )
    hass.data[DOMAIN].pop(config_entry.entry_id)

    return True
