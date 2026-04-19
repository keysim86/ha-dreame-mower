"""Support for Dreame Mower binary sensors."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    ENTITY_ID_FORMAT,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DreameMowerDataUpdateCoordinator
from .entity import DreameMowerEntity, DreameMowerEntityDescription


@dataclass
class DreameMowerBinarySensorEntityDescription(DreameMowerEntityDescription, BinarySensorEntityDescription):
    """Describes Dreame Mower binary sensor entity."""


BINARY_SENSORS: tuple[DreameMowerBinarySensorEntityDescription, ...] = (
    DreameMowerBinarySensorEntityDescription(
        key="has_saved_map",
        icon="mdi:map-check",
        value_fn=lambda value, device: device.status.has_saved_map,
        exists_fn=lambda description, device: device.capability.map,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DreameMowerBinarySensorEntityDescription(
        key="scheduled_clean",
        icon="mdi:calendar-clock",
        value_fn=lambda value, device: device.status.scheduled_clean,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Dreame Mower binary sensor based on a config entry."""
    coordinator: DreameMowerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DreameMowerBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSORS
        if description.exists_fn(description, coordinator.device)
    )


class DreameMowerBinarySensorEntity(DreameMowerEntity, BinarySensorEntity):
    """Defines a Dreame Mower binary sensor entity."""

    def __init__(
        self,
        coordinator: DreameMowerDataUpdateCoordinator,
        description: DreameMowerBinarySensorEntityDescription,
    ) -> None:
        """Initialize a Dreame Mower binary sensor entity."""
        super().__init__(coordinator, description)
        if description.key:
            self._attr_unique_id = f"{coordinator.device.mac}_{description.key}"
            self.entity_id = ENTITY_ID_FORMAT.format(
                f"{coordinator.device.name.lower().replace(' ', '_')}_{description.key}"
            )

    @property
    def is_on(self) -> bool:
        """Return true if binary sensor is on."""
        if self.entity_description.value_fn:
            return bool(self.entity_description.value_fn(None, self.device))
        return False
