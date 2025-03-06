import logging
from datetime import timedelta
import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Paperless-ngx sensor from a config entry."""
    config = config_entry.data
    url = config["url"]
    api_token = config["api_token"]

    async_add_entities([PaperlessNgxSensor(url, api_token)], True)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Paperless-ngx sensor."""
    paperless_url = config.get("url")
    api_token = config.get("api_token")
    
    if not paperless_url or not api_token:
        _LOGGER.error("URL and API token are required")
        return

    async_add_entities([PaperlessNgxSensor(paperless_url, api_token)], True)

class PaperlessNgxSensor(SensorEntity):
    """Representation of a Paperless-ngx sensor."""

    def __init__(self, url, api_token):
        """Initialize the sensor."""
        self._url = url
        self._api_token = api_token
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Paperless-ngx Documents"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor."""
        headers = {
            "Authorization": f"Token {self._api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self._url}/api/documents/", headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self._state = len(data["results"])
            self._attributes = {
                "latest_document": data["results"][0]["title"] if data["results"] else None
            }
        except requests.RequestException as err:
            _LOGGER.error("Error fetching data from Paperless-ngx: %s", err)
            self._state = None
            self._attributes = {}
