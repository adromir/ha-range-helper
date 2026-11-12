# 📏 Range Helper for Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-range-helper&category=integration)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/adromir/ha-range-helper?style=for-the-badge&color=blue)](https://github.com/adromir/ha-range-helper/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/adromir/ha-range-helper)

A lightweight, native **Home Assistant Helper Integration** that checks whether any numeric sensor (temperature, illuminance, power, battery, humidity, etc.) is **inside** or **outside** a defined numerical range (`min` and `max`), with optional hysteresis buffer and dynamic helper-based limits.

Eliminates complex two-condition `AND` / `OR` blocks or manual Jinja2 template sensors in your automations!

---

## 🎯 The Problem This Solves

In Home Assistant's visual automation editor, testing if a numeric sensor is within a range (e.g. *Temperature is between 20°C and 23°C*, or *Power is between 5 W and 150 W*) requires creating two separate conditions combined with boolean logic:
```yaml
# ❌ Clunky multi-condition workaround:
condition: and
conditions:
  - condition: numeric_state
    entity_id: sensor.living_room_temperature
    above: 20
  - condition: numeric_state
    entity_id: sensor.living_room_temperature
    below: 23
```

Testing the inverse (*Temperature is OUTSIDE 20°C - 23°C*) is even worse and requires an `OR` block or templates:
```yaml
# ❌ Tedious template condition:
condition: template
value_template: "{{ states('sensor.living_room_temperature') | float < 20 or states('sensor.living_room_temperature') | float > 23 }}"
```

With the **Range Helper**, you configure a single helper via the UI and use it directly as a standard, high-performance binary sensor:
```yaml
# ✔️ Clean, native visual editor condition:
condition: state
entity_id: binary_sensor.comfort_temperature_range
state: "on"
```

---

## ✨ Key Features & Advantages

- 🎛️ **Native Helper Integration (`integration_type: helper`)**: Directly discoverable in Home Assistant under **Settings > Devices & Services > Helpers > Create Helper > Range Helper**.
- 🔄 **Inside or Outside Range**:
  - **`Inside Range` (Default)**: Turns **ON** when `min <= value <= max`.
  - **`Outside Range`**: Turns **ON** when value is outside the comfort or threshold band.
- 🎚️ **Dynamic Limits via Entities**: Use static numbers or link `input_number.*` / `sensor.*` entities to adjust minimum or maximum limits dynamically from dashboard sliders!
- 🛡️ **Hysteresis / Noise Buffer**: Set an optional buffer zone (deadband) to prevent rapid on/off flapping when values oscillate near the threshold boundary.
- 🔲 **Inclusive or Exclusive Bounds**: Choose whether boundary limits are inclusive (`<=` / `>=`) or exclusive (`<` / `>`).
- 🎨 **Dynamic State Icons**: Set custom icons for active vs. idle states (e.g., `mdi:thermometer-check` when in range, `mdi:thermometer-alert` when out of range).
- 🏷️ **Rich Diagnostic Attributes**: Exposes `current_value`, `min_value`, `max_value`, `in_range`, and `hysteresis` right in developer tools.
- ⚙️ **100% UI Config Flow & Options Flow**: Modify all parameters on the fly without YAML restarts.
- 🌐 **Bilingual Support**: Fully localized in English and German.

---

## 📦 Installation

### Method 1: HACS (Recommended)

1. Click the button below to add this repository directly to HACS:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-range-helper&category=integration)

2. Or manually in HACS:
   - Go to **HACS** > **Integrations** > **Three dots menu (top right)** > **Custom repositories**.
   - URL: `https://github.com/adromir/ha-range-helper`
   - Type: `Integration`
   - Click **Add**, then find **Range Helper** and click **Download**.
3. **Restart Home Assistant**.

### Method 2: Manual Installation
1. Copy the `custom_components/range_helper` directory into your Home Assistant `<config>/custom_components/` folder.
2. Restart Home Assistant.

---

## 🚀 How to Use

1. In Home Assistant, navigate to **Settings** > **Devices & Services** > **Helpers**.
2. Click **Create Helper** (bottom right) and select **Range Helper**.
3. Configure your helper:
   - **Name**: e.g., `Wohlfühltemperatur Wohnzimmer`
   - **Target Entity**: e.g., `sensor.living_room_temperature`
   - **Match Mode**: `Inside Range` or `Outside Range`
   - **Minimum Limit**: e.g. `20.0` (or link an `input_number` helper)
   - **Maximum Limit**: e.g. `23.5` (or link an `input_number` helper)
   - **Hysteresis**: e.g. `0.2` (optional noise buffer)
   - **Device Class & Icons** (optional).
4. Click **Submit**. Your new binary sensor is immediately ready for automations, scripts, and dashboards!

---

## 📄 Disclaimer

This is a custom community integration and is not officially affiliated with or endorsed by Nabu Casa or Home Assistant.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

**Author**: [Adromir](https://github.com/adromir)  
Website: [https://github.com/adromir](https://github.com/adromir)

