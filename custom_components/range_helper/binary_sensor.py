"""Binary sensor platform for Range Helper."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_CURRENT_VALUE,
    ATTR_HYSTERESIS,
    ATTR_IN_RANGE,
    ATTR_INCLUSIVE,
    ATTR_MATCH_MODE,
    ATTR_MAX_ENTITY,
    ATTR_MAX_VALUE,
    ATTR_MIN_ENTITY,
    ATTR_MIN_VALUE,
    ATTR_SOURCE_ENTITY,
    CONF_ACTIVE_ICON,
    CONF_DEVICE_CLASS,
    CONF_HYSTERESIS,
    CONF_IDLE_ICON,
    CONF_INCLUSIVE,
    CONF_MATCH_MODE,
    CONF_MAX_ENTITY,
    CONF_MAX_VALUE,
    CONF_MIN_ENTITY,
    CONF_MIN_VALUE,
    CONF_SOURCE_ENTITY,
    DEFAULT_DEVICE_CLASS,
    DEFAULT_HYSTERESIS,
    DEFAULT_INCLUSIVE,
    DEFAULT_MATCH_MODE,
    DEFAULT_NAME,
    DEVICE_CLASS_NONE,
    MATCH_MODE_INSIDE,
    MATCH_MODE_OUTSIDE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Range binary sensor from config entry."""
    async_add_entities([RangeBinarySensor(entry)], True)


class RangeBinarySensor(BinarySensorEntity):
    """Representation of a Range Helper Binary Sensor."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._entry = entry
        config = {**entry.data, **entry.options}

        self._attr_name = config.get(CONF_NAME, DEFAULT_NAME)
        self._attr_unique_id = f"{entry.entry_id}_range"

        self._source_entity: str = config.get(CONF_SOURCE_ENTITY, "")
        self._match_mode: str = config.get(CONF_MATCH_MODE, DEFAULT_MATCH_MODE)

        self._static_min_value: float | None = (
            float(config[CONF_MIN_VALUE])
            if config.get(CONF_MIN_VALUE) is not None
            else None
        )
        self._min_entity: str | None = config.get(CONF_MIN_ENTITY) or None

        self._static_max_value: float | None = (
            float(config[CONF_MAX_VALUE])
            if config.get(CONF_MAX_VALUE) is not None
            else None
        )
        self._max_entity: str | None = config.get(CONF_MAX_ENTITY) or None

        self._inclusive: bool = config.get(CONF_INCLUSIVE, DEFAULT_INCLUSIVE)
        self._hysteresis: float = float(config.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))

        self._active_icon: str | None = config.get(CONF_ACTIVE_ICON) or None
        self._idle_icon: str | None = config.get(CONF_IDLE_ICON) or None

        device_class = config.get(CONF_DEVICE_CLASS, DEFAULT_DEVICE_CLASS)
        if device_class and device_class != DEVICE_CLASS_NONE:
            try:
                self._attr_device_class = BinarySensorDeviceClass(device_class)
            except ValueError:
                self._attr_device_class = None
        else:
            self._attr_device_class = None

        self._current_value: float | None = None
        self._effective_min: float | None = None
        self._effective_max: float | None = None
        self._in_range: bool | None = None

        self._attr_is_on: bool | None = None
        self._attr_available: bool = True

    @property
    def icon(self) -> str | None:
        """Return the dynamic active or idle icon."""
        if self.is_on and self._active_icon:
            return self._active_icon
        if not self.is_on and self._idle_icon:
            return self._idle_icon
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_SOURCE_ENTITY: self._source_entity,
            ATTR_CURRENT_VALUE: self._current_value,
            ATTR_MIN_VALUE: self._effective_min,
            ATTR_MIN_ENTITY: self._min_entity,
            ATTR_MAX_VALUE: self._effective_max,
            ATTR_MAX_ENTITY: self._max_entity,
            ATTR_MATCH_MODE: self._match_mode,
            ATTR_INCLUSIVE: self._inclusive,
            ATTR_HYSTERESIS: self._hysteresis,
            ATTR_IN_RANGE: self._in_range,
        }

    async def async_added_to_hass(self) -> None:
        """Register state listeners when added to hass."""
        tracked = [self._source_entity]
        if self._min_entity and self._min_entity not in tracked:
            tracked.append(self._min_entity)
        if self._max_entity and self._max_entity not in tracked:
            tracked.append(self._max_entity)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                tracked,
                self._async_tracked_state_changed,
            )
        )
        self._evaluate_state()

    @callback
    def _async_tracked_state_changed(self, event: Event) -> None:
        """Handle state change of tracked entities."""
        self._evaluate_state()
        self.async_write_ha_state()

    def _resolve_bound(self, entity_id: str | None, static_val: float | None) -> float | None:
        """Resolve numeric bound from entity or static value."""
        if entity_id:
            state = self.hass.states.get(entity_id)
            if state is not None and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                try:
                    return float(state.state)
                except (ValueError, TypeError):
                    pass
        return static_val

    @callback
    def _evaluate_state(self) -> None:
        """Evaluate numeric value against range limits."""
        source_state = self.hass.states.get(self._source_entity)
        if source_state is None or source_state.state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            self._attr_available = False
            self._attr_is_on = None
            self._current_value = None
            return

        try:
            current_num = float(source_state.state)
        except (ValueError, TypeError):
            self._attr_available = False
            self._attr_is_on = None
            self._current_value = None
            return

        self._attr_available = True
        self._current_value = current_num

        min_val = self._resolve_bound(self._min_entity, self._static_min_value)
        max_val = self._resolve_bound(self._max_entity, self._static_max_value)
        self._effective_min = min_val
        self._effective_max = max_val

        # If neither bound is set, cannot evaluate
        if min_val is None and max_val is None:
            self._attr_is_on = None
            self._in_range = None
            return

        # Hysteresis adjustment based on previous in_range state
        hyst = max(0.0, self._hysteresis)
        prev_in_range = self._in_range

        if hyst > 0.0 and prev_in_range is not None:
            if prev_in_range:
                # Value was inside range: needs to exceed buffer to exit
                eff_min = min_val - hyst if min_val is not None else None
                eff_max = max_val + hyst if max_val is not None else None
            else:
                # Value was outside range: needs to pass buffer to enter
                eff_min = min_val + hyst if min_val is not None else None
                eff_max = max_val - hyst if max_val is not None else None
        else:
            eff_min = min_val
            eff_max = max_val

        # Range condition
        if self._inclusive:
            in_range = (eff_min is None or current_num >= eff_min) and (
                eff_max is None or current_num <= eff_max
            )
        else:
            in_range = (eff_min is None or current_num > eff_min) and (
                eff_max is None or current_num < eff_max
            )

        self._in_range = in_range

        if self._match_mode == MATCH_MODE_OUTSIDE:
            self._attr_is_on = not in_range
        else:
            self._attr_is_on = in_range

