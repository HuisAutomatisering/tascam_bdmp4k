"""The Tascam BD-MP4K integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_PORT
from .coordinator import TascamConfigEntry, TascamCoordinator
from .protocol import TascamClient

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.MEDIA_PLAYER,
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TascamConfigEntry,
) -> bool:
    """Set up Tascam BD-MP4K from a config entry."""
    client = TascamClient(entry.data[CONF_HOST], entry.data[CONF_PORT])
    coordinator = TascamCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: TascamConfigEntry,
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
    if unload_ok:
        await entry.runtime_data.client.async_disconnect()
    return unload_ok
