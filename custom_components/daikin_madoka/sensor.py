"""Support for Daikin AC sensors."""
import logging

from homeassistant.const import (
    CONF_TYPE,
    CONF_UNIT_OF_MEASUREMENT,
    UnitOfTemperature
)

from homeassistant.components.sensor import (
    SensorDeviceClass
)

from homeassistant.helpers.entity import Entity

from . import DOMAIN
from .const import (
    SENSOR_TYPE_TEMPERATURE,
    CONTROLLERS,
)

from pymadoka import Controller
from pymadoka.feature import ConnectionException, ConnectionStatus

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up the Daikin sensors.

    Can only be called when a user accidentally mentions the platform in their
    config. But even in that case it would have been ignored.
    """


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Daikin climate based on config_entry."""
    ent = []
    for controller in hass.data[DOMAIN][entry.entry_id][CONTROLLERS].values():
        ent.append(MadokaSensor(controller))
    async_add_entities(ent)


class MadokaSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, controller: Controller) -> None:
        """Initialize the sensor."""
        self.controller = controller
        self._sensor = {
            CONF_TYPE: SENSOR_TYPE_TEMPERATURE,
            CONF_UNIT_OF_MEASUREMENT: UnitOfTemperature.CELSIUS,
        }
 
    @property   
    def available(self):
        """Return the availability."""
        return self.controller.connection.connection_status is ConnectionStatus.CONNECTED

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.controller.connection.address

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self.controller.connection.name if self.controller.connection.name is not None else self.controller.connection.address


    @property
    def state(self):
        """Return the internal state of the sensor."""
        if self.controller.temperatures.status is None:
            return None
        return self.controller.temperatures.status.indoor

    @property
    def device_class(self):
        """Return the class of this device."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def icon(self):
        """Return the icon of this device."""
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    async def async_update(self):
        """Retrieve latest state."""
        try:
            await self.controller.temperatures.query()
        except ConnectionAbortedError:
            pass
        except ConnectionException as e:
            # Handle specific BluZ/Bluetooth errors more gracefully
            error_msg = str(e).lower()
            if "operation already in progress" in error_msg or "br-connection-canceled" in error_msg:
                # These are common Bluetooth stack issues, log at debug level to reduce noise
                _LOGGER.debug(
                    "Bluetooth connection issue for sensor %s: %s",
                    self.name,
                    str(e),
                )
            else:
                # Other connection exceptions, log at warning level
                _LOGGER.warning(
                    "Connection issue for sensor %s: %s",
                    self.name,
                    str(e),
                )
        except Exception as e:
            # Catch any other unexpected errors
            error_msg = str(e).lower()
            if "operation already in progress" in error_msg or "br-connection-canceled" in error_msg:
                _LOGGER.debug(
                    "Bluetooth operation conflict for sensor %s: %s",
                    self.name,
                    str(e),
                )
            else:
                _LOGGER.error(
                    "Unexpected error updating sensor %s: %s",
                    self.name,
                    str(e),
                )

    @property
    async def async_device_info(self):
        """Return a device description for device registry."""
        try:
            return await self.controller.read_info()
        except ConnectionAbortedError:
            pass
        except ConnectionException:
            pass
