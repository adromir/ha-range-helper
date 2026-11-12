"""Constants for the Range Helper integration."""
from __future__ import annotations

DOMAIN = "range_helper"

CONF_SOURCE_ENTITY = "source_entity"
CONF_MIN_VALUE = "min_value"
CONF_MIN_ENTITY = "min_entity"
CONF_MAX_VALUE = "max_value"
CONF_MAX_ENTITY = "max_entity"
CONF_MATCH_MODE = "match_mode"
CONF_INCLUSIVE = "inclusive"
CONF_HYSTERESIS = "hysteresis"
CONF_DEVICE_CLASS = "device_class"
CONF_ACTIVE_ICON = "active_icon"
CONF_IDLE_ICON = "idle_icon"

DEFAULT_NAME = "Range Helper"
DEFAULT_MATCH_MODE = "inside"
DEFAULT_INCLUSIVE = True
DEFAULT_HYSTERESIS = 0.0
DEFAULT_DEVICE_CLASS = "none"

MATCH_MODE_INSIDE = "inside"
MATCH_MODE_OUTSIDE = "outside"

MATCH_MODES = [
    MATCH_MODE_INSIDE,
    MATCH_MODE_OUTSIDE,
]

DEVICE_CLASS_NONE = "none"

SUPPORTED_DEVICE_CLASSES = [
    DEVICE_CLASS_NONE,
    "battery",
    "cold",
    "heat",
    "moisture",
    "motion",
    "occupancy",
    "power",
    "presence",
    "problem",
    "running",
    "safety",
]

ATTR_SOURCE_ENTITY = "source_entity"
ATTR_CURRENT_VALUE = "current_value"
ATTR_MIN_VALUE = "min_value"
ATTR_MIN_ENTITY = "min_entity"
ATTR_MAX_VALUE = "max_value"
ATTR_MAX_ENTITY = "max_entity"
ATTR_MATCH_MODE = "match_mode"
ATTR_INCLUSIVE = "inclusive"
ATTR_HYSTERESIS = "hysteresis"
ATTR_IN_RANGE = "in_range"
