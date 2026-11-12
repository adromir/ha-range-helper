"""Config flow for Range Helper integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_SOURCE_ENTITY,
    CONF_MIN_VALUE,
    CONF_MIN_ENTITY,
    CONF_MAX_VALUE,
    CONF_MAX_ENTITY,
    CONF_MATCH_MODE,
    CONF_INCLUSIVE,
    CONF_HYSTERESIS,
    CONF_DEVICE_CLASS,
    CONF_ACTIVE_ICON,
    CONF_IDLE_ICON,
    DEFAULT_NAME,
    DEFAULT_MATCH_MODE,
    DEFAULT_INCLUSIVE,
    DEFAULT_HYSTERESIS,
    DEFAULT_DEVICE_CLASS,
    MATCH_MODES,
    SUPPORTED_DEVICE_CLASSES,
)

_LOGGER = logging.getLogger(__name__)


def _validate_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate user input fields."""
    errors: dict[str, str] = {}
    name = user_input.get(CONF_NAME, "").strip() if CONF_NAME in user_input else "valid"
    source_entity = user_input.get(CONF_SOURCE_ENTITY)

    if not name:
        errors[CONF_NAME] = "empty_name"
    if not source_entity:
        errors[CONF_SOURCE_ENTITY] = "empty_source"

    min_val = user_input.get(CONF_MIN_VALUE)
    min_ent = user_input.get(CONF_MIN_ENTITY)
    max_val = user_input.get(CONF_MAX_VALUE)
    max_ent = user_input.get(CONF_MAX_ENTITY)

    if min_val is None and not min_ent and max_val is None and not max_ent:
        errors["base"] = "no_bounds_specified"

    if (
        min_val is not None
        and max_val is not None
        and not min_ent
        and not max_ent
        and float(min_val) > float(max_val)
    ):
        errors[CONF_MIN_VALUE] = "min_greater_than_max"

    return errors


class RangeHelperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Range Helper."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Required(
                    CONF_MATCH_MODE, default=DEFAULT_MATCH_MODE
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[{"value": m, "label": m} for m in MATCH_MODES],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="match_mode",
                    )
                ),
                vol.Optional(CONF_MIN_VALUE): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(CONF_MIN_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Optional(CONF_MAX_VALUE): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(CONF_MAX_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Optional(
                    CONF_INCLUSIVE, default=DEFAULT_INCLUSIVE
                ): selector.BooleanSelector(),
                vol.Optional(
                    CONF_HYSTERESIS, default=DEFAULT_HYSTERESIS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0.0,
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(
                    CONF_DEVICE_CLASS, default=DEFAULT_DEVICE_CLASS
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": dc, "label": dc}
                            for dc in SUPPORTED_DEVICE_CLASSES
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="device_class",
                    )
                ),
                vol.Optional(CONF_ACTIVE_ICON): selector.IconSelector(),
                vol.Optional(CONF_IDLE_ICON): selector.IconSelector(),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> RangeHelperOptionsFlow:
        """Get the options flow for this handler."""
        return RangeHelperOptionsFlow(config_entry)


class RangeHelperOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Range Helper."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        current_data = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SOURCE_ENTITY,
                    default=current_data.get(CONF_SOURCE_ENTITY, ""),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Required(
                    CONF_MATCH_MODE,
                    default=current_data.get(CONF_MATCH_MODE, DEFAULT_MATCH_MODE),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[{"value": m, "label": m} for m in MATCH_MODES],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="match_mode",
                    )
                ),
                vol.Optional(
                    CONF_MIN_VALUE,
                    description={"suggested_value": current_data.get(CONF_MIN_VALUE)},
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(
                    CONF_MIN_ENTITY,
                    description={"suggested_value": current_data.get(CONF_MIN_ENTITY, "")},
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Optional(
                    CONF_MAX_VALUE,
                    description={"suggested_value": current_data.get(CONF_MAX_VALUE)},
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(
                    CONF_MAX_ENTITY,
                    description={"suggested_value": current_data.get(CONF_MAX_ENTITY, "")},
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Optional(
                    CONF_INCLUSIVE,
                    default=current_data.get(CONF_INCLUSIVE, DEFAULT_INCLUSIVE),
                ): selector.BooleanSelector(),
                vol.Optional(
                    CONF_HYSTERESIS,
                    default=current_data.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0.0,
                        mode=selector.NumberSelectorMode.BOX,
                        step="any",
                    )
                ),
                vol.Optional(
                    CONF_DEVICE_CLASS,
                    default=current_data.get(CONF_DEVICE_CLASS, DEFAULT_DEVICE_CLASS),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": dc, "label": dc}
                            for dc in SUPPORTED_DEVICE_CLASSES
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="device_class",
                    )
                ),
                vol.Optional(
                    CONF_ACTIVE_ICON,
                    description={"suggested_value": current_data.get(CONF_ACTIVE_ICON, "")},
                ): selector.IconSelector(),
                vol.Optional(
                    CONF_IDLE_ICON,
                    description={"suggested_value": current_data.get(CONF_IDLE_ICON, "")},
                ): selector.IconSelector(),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
