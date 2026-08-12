from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple


@dataclass
class Decision:
    category: str
    priority: str
    title: str
    condition: str
    action: str
    reason: str


class DecisionEngine:
    """Rule/safety engine for the simulator.

    Priority order follows the project's control philosophy:
    biological safety -> water quality -> equipment protection -> production -> energy.
    """

    def __init__(self):
        self.last_controls = {
            "water_pump": True,
            "lighting": False,
            "cooling": False,
            "ventilation": False,
            "aeration": False,
            "grid": False,
        }

    @staticmethod
    def _priority_rank(priority: str) -> int:
        return {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "OPTIMAL": 3, "INFO": 4}.get(priority, 9)

    def analyze(self, data: Dict, weather: Dict) -> List[Decision]:
        d: List[Decision] = []
        air = data["air_temperature"]
        water = data["water_temperature"]
        humidity = data["humidity"]
        ph = data["ph"]
        ec = data["ec"]
        level = data["water_level"]
        do = data["dissolved_oxygen"]
        solar = data["solar_power"]
        battery = data["battery_soc"]
        is_night = data["is_night"]
        rain = weather.get("precipitation_probability", 0)
        forecast_temp = weather.get("forecast_max_temp", air)

        if level <= 20:
            d.append(Decision("WATER", "CRITICAL", "Critical tank level", f"Water level is {level:.0f}%.",
                              "Run water pump and request water refill.",
                              "Tank reserve is critically low; energy saving is overridden by water-system protection."))
        elif level <= 35:
            d.append(Decision("WATER", "HIGH", "Low tank level", f"Water level is {level:.0f}%.",
                              "Run water pump / replenish water.",
                              "The controller protects circulation and prevents the tanks from reaching the critical zone."))
        elif is_night and level <= 50:
            d.append(Decision("WATER", "HIGH", "Night water-demand watch", f"Night level is {level:.0f}%.",
                              "Keep pump available and predict overnight demand.",
                              "At night solar generation is unavailable, so the engine checks whether the stored water reserve can cover the expected demand."))
        else:
            d.append(Decision("WATER", "NORMAL", "Water reserve sufficient", f"Tank level is {level:.0f}%.",
                              "Maintain normal circulation strategy.",
                              "There is enough water reserve to operate without an immediate refill request."))

        if do < 4.5:
            d.append(Decision("BIOLOGY", "CRITICAL", "Low dissolved oxygen", f"DO is {do:.1f} mg/L.",
                              "Start aeration and keep circulation active.",
                              "Fish health has higher priority than energy saving."))
        elif do < 5.5:
            d.append(Decision("BIOLOGY", "HIGH", "Oxygen approaching limit", f"DO is {do:.1f} mg/L.",
                              "Increase aeration readiness.",
                              "The oxygen level is below the preferred operating band."))
        else:
            d.append(Decision("BIOLOGY", "NORMAL", "Oxygen stable", f"DO is {do:.1f} mg/L.",
                              "No additional aeration required.",
                              "Dissolved oxygen is currently inside the simulated safe band."))

        if water >= 30:
            d.append(Decision("WATER QUALITY", "CRITICAL", "High water temperature", f"Water temperature is {water:.1f}°C.",
                              "Enable cooling and increase ventilation if needed.",
                              "Warm water reduces the safety margin for fish and dissolved oxygen."))
        elif water >= 28:
            d.append(Decision("WATER QUALITY", "HIGH", "Water temperature elevated", f"Water temperature is {water:.1f}°C.",
                              "Prepare cooling.",
                              "Cooling is enabled before the water reaches the critical zone."))

        if ph < 6.2:
            d.append(Decision("WATER QUALITY", "HIGH", "Low pH", f"pH is {ph:.2f}.",
                              "Flag water-quality intervention.",
                              "The simulated pH is below the configured operating boundary."))
        elif ph > 7.8:
            d.append(Decision("WATER QUALITY", "HIGH", "High pH", f"pH is {ph:.2f}.",
                              "Flag water-quality intervention.",
                              "The simulated pH is above the configured operating boundary."))

        if ec < 0.8 or ec > 2.5:
            d.append(Decision("WATER QUALITY", "HIGH", "EC outside target", f"EC is {ec:.2f} mS/cm.",
                              "Flag nutrient/water-quality check.",
                              "Electrical conductivity is outside the configured simulated band."))

        # Ventilation is deliberately conservative: humidity reaches 90% before humidity alone opens it.
        if humidity >= 90:
            d.append(Decision("CLIMATE", "HIGH", "Very high humidity", f"Humidity is {humidity:.1f}%.",
                              "Open ventilation.",
                              "Humidity has reached the 90% control threshold; ventilation is needed to reduce condensation risk."))
        elif air >= 34:
            d.append(Decision("CLIMATE", "HIGH", "High air temperature", f"Air temperature is {air:.1f}°C.",
                              "Open ventilation and cooling.",
                              "Air temperature is high enough to justify active heat removal."))
        elif air >= 31:
            d.append(Decision("CLIMATE", "NORMAL", "Warm air", f"Air temperature is {air:.1f}°C.",
                              "Keep ventilation ready.",
                              "The temperature is elevated but not yet in the critical cooling zone."))
        else:
            d.append(Decision("CLIMATE", "NORMAL", "Climate stable", f"Air temperature is {air:.1f}°C and humidity is {humidity:.0f}%.",
                              "No additional climate action.",
                              "Current climate conditions are within the configured operating envelope."))

        if forecast_temp >= 35:
            d.append(Decision("PREDICTION", "HIGH", "Hot period predicted", f"Forecast maximum is {forecast_temp:.1f}°C.",
                              "Pre-cool / prepare ventilation capacity.",
                              "The weather forecast indicates a higher thermal load ahead."))
        elif rain >= 60:
            d.append(Decision("PREDICTION", "NORMAL", "Rain probability elevated", f"Rain probability is {rain:.0f}%.",
                              "Expect lower solar availability and adjust energy planning.",
                              "Cloud/rain conditions can reduce PV production and change cooling/ventilation demand."))

        if solar >= 3.0:
            d.append(Decision("ENERGY", "OPTIMAL", "Strong solar window", f"Solar production is {solar:.1f} kW.",
                              "Use available solar energy for flexible loads.",
                              "High PV output reduces the need to draw energy from the grid."))
        elif solar < 0.4 and is_night:
            d.append(Decision("ENERGY", "NORMAL", "Night energy mode", "Solar generation is near zero.",
                              "Prioritize biological loads and defer flexible loads.",
                              "At night the system protects critical biology while minimizing non-essential consumption."))

        if battery < 20:
            d.append(Decision("ENERGY", "HIGH", "Low battery reserve", f"Battery SOC is {battery:.0f}%.",
                              "Protect battery and use grid support when required.",
                              "Battery reserve is low and should not be depleted by flexible loads."))

        return sorted(d, key=lambda x: self._priority_rank(x.priority))

    def calculate_controls(self, data: Dict, weather: Dict, decisions: List[Decision]) -> Dict[str, bool]:
        air = data["air_temperature"]
        water = data["water_temperature"]
        humidity = data["humidity"]
        level = data["water_level"]
        do = data["dissolved_oxygen"]
        solar = data["solar_power"]
        battery = data["battery_soc"]
        is_night = data["is_night"]

        critical_biology = do < 4.5 or level <= 20
        pump = True
        if not critical_biology:
            # Pump is normally on, but can be duty-cycled when water reserve is high.
            if level >= 72 and is_night and battery < 35:
                pump = False
            elif level >= 85 and solar < 0.3 and battery < 25:
                pump = False
            else:
                pump = True

        ventilation = humidity >= 90 or air >= 34
        cooling = water >= 28 or air >= 34
        aeration = do < 5.5 or water >= 29

        # Lighting is flexible: use it when the farm is in its simulated lighting window and solar is weak.
        lighting = (not is_night and solar < 1.0) or (is_night and data["plant_light_need"])
        if battery < 25 and not critical_biology:
            lighting = False

        # Grid is support, not a primary optimization target.
        grid = battery < 25 or (solar < 0.5 and (pump or cooling or aeration or lighting))

        self.last_controls = {
            "water_pump": pump,
            "lighting": lighting,
            "cooling": cooling,
            "ventilation": ventilation,
            "aeration": aeration,
            "grid": grid,
        }
        return self.last_controls.copy()

    def prediction(self, data: Dict, weather: Dict) -> Dict:
        level = data["water_level"]
        humidity = data["humidity"]
        air = data["air_temperature"]
        water = data["water_temperature"]
        solar = data["solar_power"]
        rain = weather.get("precipitation_probability", 0)
        forecast_max = weather.get("forecast_max_temp", air)

        # Simple physics-like forecast, not a trained ML model.
        evap = max(0.0, (air - 22) * 0.18) + max(0.0, (70 - humidity) * 0.025)
        plant_demand = 2.2 if air < 28 else 3.2 if air < 33 else 4.3
        weather_adjust = 0.7 if rain >= 70 else 1.0
        six_hour_demand = round((evap + plant_demand) * 6 * weather_adjust, 1)
        level_after = max(0.0, level - six_hour_demand / 1.8)
        hours_to_35 = round(max(0.0, (level - 35) / max(0.4, (evap + plant_demand) / 1.8)), 1)

        if level_after < 35:
            water_forecast = "Refill likely within the next 6 hours"
        elif level_after < 50:
            water_forecast = "Monitor water reserve closely"
        else:
            water_forecast = "Water reserve expected to remain adequate"

        if forecast_max >= 35 or water >= 28:
            thermal_risk = "HIGH"
        elif forecast_max >= 32 or water >= 26:
            thermal_risk = "MODERATE"
        else:
            thermal_risk = "LOW"

        solar_outlook = "Strong" if solar >= 3.0 else "Moderate" if solar >= 1.0 else "Weak"

        return {
            "six_hour_water_demand_l": six_hour_demand,
            "predicted_level_6h": round(level_after, 1),
            "hours_to_35_percent": hours_to_35,
            "water_forecast": water_forecast,
            "thermal_risk": thermal_risk,
            "solar_outlook": solar_outlook,
        }
