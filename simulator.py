import math
import random
from datetime import datetime
from typing import Dict


class FarmSimulator:
    """Physics-like farm simulator with realistic operating limits and scenario injection."""

    SCENARIOS = [
        "Normal", "High Solar", "Low Solar", "High Air Temperature", "High Humidity",
        "Low Water Level", "Critical Water Level", "Low pH", "High pH", "High Water Temperature",
        "Low Oxygen", "Pump Failure", "Low Battery", "Critical Farm Condition"
    ]

    def __init__(self):
        self.water_pump = True
        self.lighting = False
        self.cooling = False
        self.ventilation = False
        self.aeration = False
        self.grid_connected = False
        self.scenario = "Normal"
        self.water_level = 80.0
        self.battery_soc = 80.0
        self.step_count = 0
        self.scenario_once = False

    @staticmethod
    def _clip(v, low, high):
        return max(low, min(high, v))

    def reset(self):
        self.__init__()

    def apply_scenario(self, scenario: str):
        self.scenario = scenario
        self.scenario_once = True

    def _solar_profile(self, hour: int, minute: int) -> float:
        h = hour + minute / 60
        if h < 6 or h > 18.5:
            return 0.0
        # Smooth bell around solar noon, max about 5.8 kW.
        x = (h - 12.25) / 6.2
        return max(0.0, 5.8 * math.exp(-(x * x)))

    def update(self, weather: Dict | None = None) -> Dict:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        is_night = hour < 6 or hour >= 19
        self.step_count += 1

        weather_temp = weather.get("current_temperature", 28) if weather else 28
        weather_humidity = weather.get("current_humidity", 55) if weather else 55
        weather_wind = weather.get("wind_speed", 12) if weather else 12

        base_air = weather_temp + (2.0 if 10 <= hour <= 16 else -1.0)
        air = base_air + random.gauss(0, 0.45)
        air = self._clip(air, 15, 42)

        water = 23.5 + 0.22 * (air - 24) + random.gauss(0, 0.15)
        water = self._clip(water, 18, 32)

        humidity = weather_humidity + random.gauss(0, 2.0)
        humidity += 3 if is_night else -2
        humidity = self._clip(humidity, 30, 95)

        ph = 6.8 + random.gauss(0, 0.035)
        ec = 1.5 + random.gauss(0, 0.035)

        # Water balance: pump circulation restores some reserve; plants/evaporation consume it.
        evaporation = max(0.04, (air - 18) * 0.012 + (70 - humidity) * 0.002)
        plant_use = 0.10 if air < 28 else 0.16 if air < 33 else 0.22
        pump_return = 0.30 if self.water_pump else 0.0
        self.water_level += pump_return - evaporation - plant_use + random.gauss(0, 0.05)
        self.water_level = self._clip(self.water_level, 5, 98)

        solar = self._solar_profile(hour, minute) + random.gauss(0, 0.12)
        solar = self._clip(solar, 0, 6.0)
        if self.scenario == "High Solar":
            solar = self._clip(solar + 1.2, 0, 6.0)
        elif self.scenario == "Low Solar":
            solar *= 0.25

        do = 6.7 - max(0, water - 26) * 0.45 + (0.7 if self.aeration else 0) + random.gauss(0, 0.18)
        do = self._clip(do, 3.5, 9.5)

        # Battery balance in % per simulation cycle.
        generation = solar * 0.035
        loads = 0.9 * self.water_pump + 1.0 * self.lighting + 1.6 * self.cooling + 0.35 * self.aeration
        battery_delta = generation - loads * 0.018
        self.battery_soc += battery_delta + random.gauss(0, 0.08)
        if self.grid_connected:
            self.battery_soc += 0.35
        self.battery_soc = self._clip(self.battery_soc, 10, 100)

        pump_current = 3.0 + random.gauss(0, 0.08) if self.water_pump else 0.25 + random.gauss(0, 0.03)
        if self.scenario == "Pump Failure":
            pump_current = 0.12

        # Scenario overrides: intentionally realistic, bounded, and correlated.
        if self.scenario == "High Air Temperature":
            air = random.uniform(34, 39)
        elif self.scenario == "High Humidity":
            humidity = random.uniform(90, 95)
        elif self.scenario == "Low Water Level":
            self.water_level = random.uniform(25, 35)
        elif self.scenario == "Critical Water Level":
            self.water_level = random.uniform(10, 20)
        elif self.scenario == "Low pH":
            ph = random.uniform(5.9, 6.2)
        elif self.scenario == "High pH":
            ph = random.uniform(7.8, 8.1)
        elif self.scenario == "High Water Temperature":
            water = random.uniform(28.5, 31.0)
        elif self.scenario == "Low Oxygen":
            do = random.uniform(3.8, 5.2)
        elif self.scenario == "Low Battery":
            self.battery_soc = random.uniform(15, 25)
        elif self.scenario == "Critical Farm Condition":
            self.water_level = random.uniform(12, 20)
            do = random.uniform(3.7, 4.6)
            air = random.uniform(35, 39)
            humidity = random.uniform(90, 95)

        # Once injected, return to normal trend on the next reading.
        if self.scenario_once and self.scenario != "Normal":
            self.scenario_once = False
        elif self.scenario != "Normal":
            self.scenario = "Normal"

        plant_light_need = (hour >= 18 or hour < 6)

        return {
            "timestamp": now,
            "air_temperature": round(air, 2),
            "water_temperature": round(water, 2),
            "humidity": round(humidity, 2),
            "ph": round(ph, 2),
            "ec": round(ec, 2),
            "water_level": round(self.water_level, 2),
            "dissolved_oxygen": round(do, 2),
            "solar_power": round(solar, 2),
            "battery_soc": round(self.battery_soc, 1),
            "pump_current": round(pump_current, 2),
            "wind_speed": round(weather_wind + random.gauss(0, 1.0), 1),
            "is_night": is_night,
            "plant_light_need": plant_light_need,
            "scenario": self.scenario,
            "controls": {
                "water_pump": self.water_pump,
                "lighting": self.lighting,
                "cooling": self.cooling,
                "ventilation": self.ventilation,
                "aeration": self.aeration,
                "grid": self.grid_connected,
            },
        }
