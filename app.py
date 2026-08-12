
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from decision_engine import DecisionEngine
from simulator import FarmSimulator
from weather_engine import EGYPT_LOCATIONS, get_weather


# ============================================================
# PAGE
# ============================================================
st.set_page_config(
    page_title="AI Resource Optimizer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# Streamlit only — no external frontend framework.
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --ink: #172033;
        --muted: #667085;
        --soft: #f5f8f7;
        --card: rgba(255,255,255,.90);
        --line: #e7ece9;
        --green: #18a66a;
        --green-dark: #087443;
        --green-soft: #e9f8f0;
        --blue: #3d82f6;
        --blue-soft: #edf5ff;
        --amber: #d98a16;
        --amber-soft: #fff7e8;
        --red: #d94b4b;
        --red-soft: #fff0f0;
        --shadow: 0 12px 35px rgba(24, 42, 35, .08);
    }

    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(48, 186, 124, .10), transparent 28%),
            radial-gradient(circle at 92% 18%, rgba(61, 130, 246, .08), transparent 25%),
            linear-gradient(180deg, #fbfdfc 0%, #f5f8f7 100%);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(255,255,255,.70);
        backdrop-filter: blur(12px);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f4f8f6 100%);
        border-right: 1px solid #e8eeeb;
    }

    [data-testid="stSidebar"] * {
        color: var(--ink);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        font-family: "Manrope", sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -.025em;
    }

    h1 {
        font-weight: 800 !important;
    }

    h2, h3 {
        font-weight: 750 !important;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 22px 0 12px;
        font-family: "Manrope", sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--ink);
    }

    .section-title span {
        width: 8px;
        height: 28px;
        border-radius: 99px;
        background: linear-gradient(180deg, #22bd7b, #087443);
        display: inline-block;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 28px;
        min-height: 265px;
        padding: 34px 38px;
        margin-bottom: 18px;
        color: white;
        background:
            linear-gradient(90deg, rgba(5,45,32,.93) 0%, rgba(9,86,57,.82) 52%, rgba(9,86,57,.34) 100%),
            url("https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1800&q=85") center/cover;
        box-shadow: 0 22px 50px rgba(7, 76, 48, .18);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 340px;
        height: 340px;
        right: -100px;
        top: -140px;
        border-radius: 50%;
        background: rgba(255,255,255,.12);
        animation: floatOrb 7s ease-in-out infinite;
    }

    @keyframes floatOrb {
        0%, 100% { transform: translate3d(0,0,0) scale(1); }
        50% { transform: translate3d(-20px,18px,0) scale(1.08); }
    }

    .hero-kicker {
        position: relative;
        z-index: 2;
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        opacity: .82;
        margin-bottom: 9px;
    }

    .hero-title {
        position: relative;
        z-index: 2;
        font-family: "Manrope", sans-serif;
        font-size: clamp(2rem, 4vw, 3.45rem);
        line-height: 1.02;
        font-weight: 800;
        letter-spacing: -.045em;
        max-width: 760px;
    }

    .hero-subtitle {
        position: relative;
        z-index: 2;
        max-width: 700px;
        margin-top: 13px;
        font-size: 1rem;
        line-height: 1.65;
        color: rgba(255,255,255,.88);
    }

    .online-pill {
        position: relative;
        z-index: 3;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 20px;
        padding: 8px 13px;
        border: 1px solid rgba(255,255,255,.18);
        border-radius: 999px;
        background: rgba(255,255,255,.10);
        backdrop-filter: blur(10px);
        font-size: .78rem;
        font-weight: 700;
    }

    .online-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #57e79f;
        box-shadow: 0 0 0 5px rgba(87,231,159,.13);
        animation: pulseDot 2s infinite;
    }

    @keyframes pulseDot {
        0%,100% { box-shadow: 0 0 0 4px rgba(87,231,159,.10); }
        50% { box-shadow: 0 0 0 8px rgba(87,231,159,.02); }
    }

    .kpi-card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 19px 20px;
        min-height: 116px;
        box-shadow: var(--shadow);
        transition: transform .2s ease, box-shadow .2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 42px rgba(24,42,35,.12);
    }

    .kpi-label {
        color: var(--muted);
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .07em;
    }

    .kpi-value {
        margin-top: 8px;
        font-family: "Manrope", sans-serif;
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--ink);
    }

    .kpi-note {
        margin-top: 5px;
        font-size: .76rem;
        color: var(--green-dark);
        font-weight: 600;
    }

    .panel {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 21px;
        box-shadow: var(--shadow);
        height: 100%;
    }

    .panel-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .panel-title {
        font-family: "Manrope", sans-serif;
        font-size: 1rem;
        font-weight: 800;
        color: var(--ink);
    }

    .panel-caption {
        font-size: .76rem;
        color: var(--muted);
    }

    .sensor-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
    }

    .sensor-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 17px;
        padding: 15px 14px;
        min-height: 112px;
        box-shadow: 0 7px 22px rgba(24,42,35,.055);
        transition: transform .18s ease, box-shadow .18s ease;
    }

    .sensor-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(24,42,35,.09);
    }

    .sensor-card-top {
        display: flex;
        align-items: center;
        gap: 9px;
        margin-bottom: 10px;
    }

    .sensor-icon {
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        background: #f0f8f4;
        font-size: 1.05rem;
    }

    .sensor-name {
        color: #344054;
        font-size: .78rem;
        font-weight: 700;
    }

    .sensor-value {
        font-family: "Manrope", sans-serif;
        font-size: 1.18rem;
        font-weight: 800;
        color: var(--ink);
    }

    .sensor-unit {
        margin-left: 4px;
        font-size: .70rem;
        color: var(--muted);
        font-weight: 600;
    }

    .weather-card-native {
        background: rgba(255,255,255,.96);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 21px;
        box-shadow: var(--shadow);
        height: 100%;
    }

    .weather-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 14px;
    }

    .weather-title {
        font-family: "Manrope", sans-serif;
        font-size: 1rem;
        font-weight: 800;
        color: var(--ink);
    }

    .weather-source {
        margin-top: 4px;
        color: var(--muted);
        font-size: .70rem;
    }

    .weather-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }

    .weather-item {
        background: #f8fbfa;
        border: 1px solid #e9f0ed;
        border-radius: 16px;
        padding: 14px;
        min-height: 78px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .weather-item.current {
        grid-column: span 2;
        min-height: 96px;
        background: linear-gradient(135deg, #f4fbf7, #f8fbff);
    }

    .weather-item-label {
        color: var(--muted);
        font-size: .66rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
    }

    .weather-item-value {
        margin-top: 5px;
        font-family: "Manrope", sans-serif;
        font-size: 1.12rem;
        font-weight: 800;
        color: var(--ink);
    }

    .weather-current-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .weather-current-icon {
        font-size: 2rem;
    }

    .weather-description {
        margin-top: 3px;
        color: var(--muted);
        font-size: .74rem;
    }

    .control-card {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 19px;
        padding: 17px;
        box-shadow: 0 8px 26px rgba(24,42,35,.06);
        height: 100%;
        transition: transform .2s ease;
    }

    .control-card:hover {
        transform: translateY(-2px);
    }

    .control-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .control-icon {
        font-size: 1.4rem;
    }

    .control-name {
        margin-top: 7px;
        font-weight: 800;
        font-size: .88rem;
    }

    .state-on, .state-off {
        padding: 5px 9px;
        border-radius: 999px;
        font-size: .68rem;
        font-weight: 800;
    }

    .state-on {
        background: var(--green-soft);
        color: var(--green-dark);
    }

    .state-off {
        background: #f1f3f4;
        color: #667085;
    }

    .control-reason {
        margin-top: 13px;
        color: var(--muted);
        font-size: .74rem;
        line-height: 1.55;
        min-height: 45px;
    }

    .info-box {
        background: var(--blue-soft);
        border: 1px solid #dbeaff;
        border-radius: 17px;
        padding: 15px 17px;
        color: #214f87;
        font-size: .82rem;
        line-height: 1.55;
    }

    .decision {
        background: #fff;
        border: 1px solid var(--line);
        border-left: 5px solid #18a66a;
        border-radius: 17px;
        padding: 15px 17px;
        margin-bottom: 10px;
        box-shadow: 0 7px 24px rgba(24,42,35,.05);
    }

    .decision-high { border-left-color: var(--amber); }
    .decision-critical { border-left-color: var(--red); }
    .decision-optimal { border-left-color: var(--blue); }

    .decision-title {
        font-weight: 800;
        font-size: .88rem;
    }

    .decision-meta {
        color: var(--muted);
        font-size: .72rem;
        margin-top: 4px;
    }

    .decision-text {
        margin-top: 8px;
        color: #344054;
        font-size: .78rem;
        line-height: 1.55;
    }

    .prediction-card {
        background: linear-gradient(145deg, #0c6f48 0%, #0b9861 100%);
        color: white;
        border-radius: 22px;
        padding: 21px;
        min-height: 170px;
        box-shadow: 0 16px 38px rgba(11,125,77,.18);
    }

    .prediction-label {
        color: rgba(255,255,255,.72);
        font-size: .7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .prediction-value {
        margin-top: 8px;
        font-family: "Manrope", sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .prediction-note {
        margin-top: 7px;
        font-size: .76rem;
        line-height: 1.5;
        color: rgba(255,255,255,.82);
    }

    .timeline-item {
        display: grid;
        grid-template-columns: 72px 1fr;
        gap: 14px;
        padding: 13px 0;
        border-bottom: 1px solid #edf1ef;
    }

    .timeline-time {
        color: var(--muted);
        font-size: .72rem;
        font-weight: 700;
        padding-top: 2px;
    }

    .timeline-title {
        font-size: .82rem;
        font-weight: 800;
    }

    .timeline-detail {
        color: var(--muted);
        font-size: .74rem;
        margin-top: 3px;
    }

    .footer-note {
        text-align: center;
        color: #98a2b3;
        font-size: .7rem;
        padding: 25px 0 10px;
    }

    div[data-testid="stMetric"] {
        background: transparent;
    }

    button[kind="primary"] {
        border-radius: 12px !important;
        font-weight: 800 !important;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
    }

    .stSelectbox > div > div,
    .stTextInput > div > div {
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--line) !important;
        border-radius: 15px !important;
        background: white !important;
    }

    @media (max-width: 900px) {
        .hero {
            padding: 25px;
            min-height: 230px;
        }
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# STATE
# ============================================================
def init_state():
    defaults = {
        "logged_in": False,
        "simulator": FarmSimulator(),
        "engine": DecisionEngine(),
        "sensor_data": None,
        "weather": None,
        "weather_location": "Cairo",
        "history": [],
        "timeline": [],
        "mode": "AUTO",
        "manual_controls": {
            "water_pump": True,
            "lighting": False,
            "cooling": False,
            "ventilation": False,
            "aeration": False,
            "grid": False,
        },
        "energy_baseline_kwh": 0.0,
        "energy_actual_kwh": 0.0,
        "water_managed_l": 0.0,
        "cycle_count": 0,
        "last_update": None,
        "last_controls": {
            "water_pump": True,
            "lighting": False,
            "cooling": False,
            "ventilation": False,
            "aeration": False,
            "grid": False,
        },
        "selected_decision": None,
        "live_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ============================================================
# LOGIN
# ============================================================
def login_page():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Solar Aquaponics Intelligence Platform</div>
            <div class="hero-title">Welcome to AI Resource Optimizer</div>
            <div class="hero-subtitle">
                Monitor your farm, understand every decision, predict resource demand,
                and optimize energy and water use from one intelligent dashboard.
            </div>
            <div class="online-pill">
                <span class="online-dot"></span>
                DEMO ENVIRONMENT
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.05, 1])

    with center:
        st.markdown("### Secure Demo Access")
        st.caption("Use the demonstration credentials to enter the platform.")

        username = st.text_input("Username", value="", placeholder="Username")
        password = st.text_input("Password", value="", type="password", placeholder="Password")

        if st.button("🚀 Enter Platform", type="primary", use_container_width=True):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.info("Demo credentials: **admin / 1234**")

    st.markdown(
        '<div class="footer-note">AI Resource Optimizer • Solar-powered aquaponics decision-support prototype</div>',
        unsafe_allow_html=True,
    )


if not st.session_state.logged_in:
    login_page()
    st.stop()


# ============================================================
# ENGINE HELPERS
# ============================================================
def refresh_weather(force=False):
    current = st.session_state.weather
    location = st.session_state.weather_location

    if force or current is None or current.get("location") != location:
        st.session_state.weather = get_weather(location)


def run_cycle():
    refresh_weather()

    sim = st.session_state.simulator
    engine = st.session_state.engine

    data = sim.update(st.session_state.weather)
    decisions = engine.analyze(data, st.session_state.weather)
    auto_controls = engine.calculate_controls(data, st.session_state.weather, decisions)

    if st.session_state.mode == "AUTO":
        controls = auto_controls
    else:
        controls = st.session_state.manual_controls.copy()

    sim.water_pump = controls["water_pump"]
    sim.lighting = controls["lighting"]
    sim.cooling = controls["cooling"]
    sim.ventilation = controls["ventilation"]
    sim.aeration = controls["aeration"]
    sim.grid_connected = controls["grid"]

    interval_h = 40 / 3600
    baseline_kw = 0.9 + 1.0 + 1.6 + 0.35
    actual_kw = (
        0.9 * controls["water_pump"]
        + 1.0 * controls["lighting"]
        + 1.6 * controls["cooling"]
        + 0.35 * controls["aeration"]
    )

    st.session_state.energy_baseline_kwh += baseline_kw * interval_h
    st.session_state.energy_actual_kwh += actual_kw * interval_h

    if controls["water_pump"]:
        st.session_state.water_managed_l += 0.9 * interval_h * 60

    st.session_state.sensor_data = data
    st.session_state.last_controls = controls.copy()
    st.session_state.cycle_count += 1
    st.session_state.last_update = datetime.now()

    for decision in decisions[:8]:
        st.session_state.timeline.insert(
            0,
            {
                "time": data["timestamp"].strftime("%H:%M:%S"),
                "priority": decision.priority,
                "category": decision.category,
                "title": decision.title,
                "condition": decision.condition,
                "action": decision.action,
                "reason": decision.reason,
            },
        )

    st.session_state.timeline = st.session_state.timeline[:30]

    st.session_state.history.append(
        {
            "Time": data["timestamp"],
            "Air °C": data["air_temperature"],
            "Water °C": data["water_temperature"],
            "Humidity %": data["humidity"],
            "pH": data["ph"],
            "EC": data["ec"],
            "Water Level %": data["water_level"],
            "DO mg/L": data["dissolved_oxygen"],
            "Solar kW": data["solar_power"],
            "Battery %": data["battery_soc"],
        }
    )

    st.session_state.history = st.session_state.history[-100:]
    return data, decisions, controls


def reset_farm():
    st.session_state.simulator = FarmSimulator()
    st.session_state.engine = DecisionEngine()
    st.session_state.sensor_data = None
    st.session_state.history = []
    st.session_state.timeline = []
    st.session_state.energy_baseline_kwh = 0.0
    st.session_state.energy_actual_kwh = 0.0
    st.session_state.water_managed_l = 0.0
    st.session_state.cycle_count = 0
    st.session_state.last_update = None
    st.session_state.selected_decision = None
    st.session_state.manual_controls = {
        "water_pump": True,
        "lighting": False,
        "cooling": False,
        "ventilation": False,
        "aeration": False,
        "grid": False,
    }


def priority_class(priority):
    return {
        "HIGH": "decision-high",
        "CRITICAL": "decision-critical",
        "OPTIMAL": "decision-optimal",
    }.get(priority, "")


def control_reason(name, data, weather):
    reasons = {
        "water_pump": (
            f"Water level {data['water_level']:.0f}% • "
            f"DO {data['dissolved_oxygen']:.1f} mg/L • "
            "circulation has biological priority."
        ),
        "lighting": (
            f"Solar {data['solar_power']:.1f} kW • "
            f"battery {data['battery_soc']:.0f}% • "
            "lighting is treated as a flexible load."
        ),
        "cooling": (
            f"Air {data['air_temperature']:.1f}°C • "
            f"water {data['water_temperature']:.1f}°C • "
            "cooling responds to thermal thresholds."
        ),
        "ventilation": (
            f"Humidity {data['humidity']:.0f}% • "
            f"air {data['air_temperature']:.1f}°C • "
            "ventilation opens at the configured climate limits."
        ),
        "aeration": (
            f"DO {data['dissolved_oxygen']:.1f} mg/L • "
            f"water {data['water_temperature']:.1f}°C • "
            "fish health has priority over energy saving."
        ),
        "grid": (
            f"Battery {data['battery_soc']:.0f}% • "
            f"solar {data['solar_power']:.1f} kW • "
            "grid is support when renewable energy is insufficient."
        ),
    }
    return reasons[name]


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌱 AI Resource Optimizer")
    st.caption("Farm control center")

    st.markdown("### Operating Mode")
    mode = st.radio(
        "Mode",
        ["AUTO", "MANUAL TEST"],
        index=0 if st.session_state.mode == "AUTO" else 1,
        label_visibility="collapsed",
    )

    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.rerun()

    st.divider()

    st.markdown("### 📍 Farm Location")
    locations = list(EGYPT_LOCATIONS.keys())
    location = st.selectbox(
        "Location",
        locations,
        index=locations.index(st.session_state.weather_location),
        label_visibility="collapsed",
    )

    if location != st.session_state.weather_location:
        st.session_state.weather_location = location
        st.session_state.weather = None
        st.rerun()

    if st.button("🌦️ Refresh Weather", use_container_width=True):
        refresh_weather(force=True)
        st.rerun()

    st.divider()

    st.markdown("### 🧪 Test Scenario")
    scenario = st.selectbox(
        "Scenario",
        FarmSimulator.SCENARIOS,
        label_visibility="collapsed",
    )

    if st.button("Generate Reading", use_container_width=True):
        st.session_state.simulator.apply_scenario(scenario)
        run_cycle()
        st.rerun()

    if st.button("Reset Farm", use_container_width=True):
        reset_farm()
        st.rerun()

    st.divider()

    st.markdown("### 🎛 Manual Controls")

    if mode == "MANUAL TEST":
        labels = [
            ("water_pump", "💧 Water Pump"),
            ("lighting", "💡 Lighting"),
            ("cooling", "❄️ Cooling"),
            ("ventilation", "🌬️ Ventilation"),
            ("aeration", "🫧 Aeration"),
            ("grid", "⚡ Grid Support"),
        ]

        for key, label in labels:
            st.session_state.manual_controls[key] = st.toggle(
                label,
                value=st.session_state.manual_controls[key],
            )

        st.caption(
            "Manual mode controls actuators only. Sensors, weather and prediction remain active."
        )
    else:
        st.caption(
            "AUTO mode lets the decision engine select actuator states from farm and weather conditions."
        )

    st.divider()

    st.markdown("### Live Simulation")
    st.session_state.live_mode = st.toggle(
        "Live updates",
        value=st.session_state.live_mode,
    )

    st.caption("Simulation interval: 40 seconds")
    st.caption("Decision engine: safety-first rule prototype")
    st.caption("Prediction: physics-inspired prototype")

    st.divider()

    if st.button("↪️ Log out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.live_mode = False
        st.rerun()


# ============================================================
# FIRST CYCLE
# ============================================================
if st.session_state.sensor_data is None:
    run_cycle()

refresh_weather()

data = st.session_state.sensor_data
weather = st.session_state.weather

prediction = st.session_state.engine.prediction(data, weather)

saved_pct = 0.0
if st.session_state.energy_baseline_kwh > 0:
    saved_pct = max(
        0.0,
        (
            1
            - st.session_state.energy_actual_kwh
            / st.session_state.energy_baseline_kwh
        )
        * 100,
    )


# ============================================================
# HERO
# ============================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">Solar Aquaponics Intelligence Platform</div>
        <div class="hero-title">AI Resource Optimizer</div>
        <div class="hero-subtitle">
            Intelligent monitoring, prediction and control for a solar-powered aquaponics farm.
            The system prioritizes biological safety first, then water quality, equipment protection,
            production and energy optimization.
        </div>
        <div class="online-pill">
            <span class="online-dot"></span>
            SYSTEM ONLINE&nbsp;&nbsp;•&nbsp;&nbsp;{st.session_state.mode} MODE&nbsp;&nbsp;•&nbsp;&nbsp;{weather["location"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPI STRIP
# ============================================================
st.markdown('<div class="section-title"><span></span>Farm Performance</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">⚡ Energy</div>
            <div class="kpi-value">{saved_pct:.0f}% saved</div>
            <div class="kpi-note">vs simulated baseline</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">💧 Water</div>
            <div class="kpi-value">{st.session_state.water_managed_l:.1f} L</div>
            <div class="kpi-note">managed by circulation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        """
        <div class="kpi-card">
            <div class="kpi-label">🐟 Fish</div>
            <div class="kpi-value">3 tanks</div>
            <div class="kpi-note">biological monitoring active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        """
        <div class="kpi-card">
            <div class="kpi-label">🌱 Plants</div>
            <div class="kpi-value">6 beds</div>
            <div class="kpi-note">recirculating production active</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LIVE CONDITIONS
# ============================================================
st.markdown('<div class="section-title"><span></span>Live Farm Conditions</div>', unsafe_allow_html=True)

left, right = st.columns([1.05, .95])

with left:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-head">
                <div>
                    <div class="panel-title">🌡 Live Sensor Data</div>
                    <div class="panel-caption">Latest simulated farm telemetry</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    sensor_rows = [
        ("🌡️", "Air Temperature", data["air_temperature"], "°C"),
        ("💧", "Water Temperature", data["water_temperature"], "°C"),
        ("💦", "Humidity", data["humidity"], "%"),
        ("🧪", "pH", data["ph"], ""),
        ("⚗️", "EC", data["ec"], "mS/cm"),
        ("📏", "Water Level", data["water_level"], "%"),
        ("🐟", "Dissolved Oxygen", data["dissolved_oxygen"], "mg/L"),
        ("⚡", "Pump Current", data["pump_current"], "A"),
        ("🔋", "Battery SOC", data["battery_soc"], "%"),
        ("☀️", "Solar Power", data["solar_power"], "kW"),
    ]

    # Use native Streamlit columns so every sensor is a real independent card.
    # This fixes the issue where separate st.markdown calls cannot remain
    # children of one HTML/CSS grid container.
    for row_start in range(0, len(sensor_rows), 4):
        cols = st.columns(4, gap="small")
        for col, (icon, name, value, unit) in zip(cols, sensor_rows[row_start:row_start + 4]):
            with col:
                st.markdown(
                    f"""
                    <div class="sensor-card">
                        <div class="sensor-card-top">
                            <div class="sensor-icon">{icon}</div>
                            <div class="sensor-name">{name}</div>
                        </div>
                        <div class="sensor-value">
                            {value:.2f}<span class="sensor-unit">{unit}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        f"""
        <div class="weather-card-native">
            <div class="weather-head">
                <div>
                    <div class="weather-title">☀️ Weather — {weather["location"]}</div>
                    <div class="weather-source">{weather["source"]}</div>
                </div>
            </div>
            <div class="weather-grid">
                <div class="weather-item current">
                    <div class="weather-current-row">
                        <div class="weather-current-icon">☀️</div>
                        <div>
                            <div class="weather-item-value" style="font-size:1.55rem; margin-top:0;">{weather["current_temperature"]:.1f}°C</div>
                            <div class="weather-description">{weather["description"]}</div>
                        </div>
                    </div>
                </div>
                <div class="weather-item">
                    <div class="weather-item-label">Humidity</div>
                    <div class="weather-item-value">{weather["current_humidity"]:.0f}%</div>
                </div>
                <div class="weather-item">
                    <div class="weather-item-label">Rain Probability</div>
                    <div class="weather-item-value">{weather["precipitation_probability"]:.0f}%</div>
                </div>
                <div class="weather-item">
                    <div class="weather-item-label">Wind</div>
                    <div class="weather-item-value">{weather["wind_speed"]:.1f} km/h</div>
                </div>
                <div class="weather-item">
                    <div class="weather-item-label">Forecast Max</div>
                    <div class="weather-item-value">{weather["forecast_max_temp"]:.1f}°C</div>
                </div>
                <div class="weather-item">
                    <div class="weather-item-label">Sunrise</div>
                    <div class="weather-item-value">{weather["sunrise"]}</div>
                </div>
                <div class="weather-item">
                    <div class="weather-item-label">Sunset</div>
                    <div class="weather-item-value">{weather["sunset"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CONTROLS
# ============================================================
st.markdown('<div class="section-title"><span></span>Farm Control Status</div>', unsafe_allow_html=True)

control_items = [
    ("water_pump", "💧", "Water Pump"),
    ("lighting", "💡", "Lighting"),
    ("cooling", "❄️", "Cooling"),
    ("ventilation", "🌬️", "Ventilation"),
    ("aeration", "🫧", "Aeration"),
    ("grid", "⚡", "Grid Support"),
]

cols = st.columns(6)

for col, (name, icon, label) in zip(cols, control_items):
    state = st.session_state.last_controls[name]

    with col:
        state_html = (
            '<span class="state-on">● ON</span>'
            if state
            else '<span class="state-off">● OFF</span>'
        )

        st.markdown(
            f"""
            <div class="control-card">
                <div class="control-top">
                    <div class="control-icon">{icon}</div>
                    {state_html}
                </div>
                <div class="control-name">{label}</div>
                <div class="control-reason">{control_reason(name, data, weather)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Why?",
            key=f"why_{name}",
            use_container_width=True,
        ):
            st.session_state.selected_decision = name

if st.session_state.selected_decision:
    name = st.session_state.selected_decision
    labels = dict((x[0], x[2]) for x in control_items)

    with st.expander(
        f"Decision Details — {labels[name]}",
        expanded=True,
    ):
        st.write(f"### {labels[name]}")

        if name == "water_pump":
            st.write(
                f"**Water level:** {data['water_level']:.1f}%  •  "
                f"**DO:** {data['dissolved_oxygen']:.1f} mg/L"
            )
            st.write(
                "The pump protects circulation and water availability. "
                "Biological safety overrides energy-saving when the reserve or oxygen level becomes critical."
            )
        elif name == "lighting":
            st.write(
                f"**Solar:** {data['solar_power']:.2f} kW  •  "
                f"**Battery:** {data['battery_soc']:.0f}%"
            )
            st.write(
                "Lighting is treated as a flexible electrical load. "
                "The controller prefers available renewable energy and protects the battery when reserve is low."
            )
        elif name == "cooling":
            st.write(
                f"**Air:** {data['air_temperature']:.1f}°C  •  "
                f"**Water:** {data['water_temperature']:.1f}°C"
            )
            st.write(
                "Cooling is enabled when the simulated thermal limits are reached. "
                "Water temperature is especially important because fish safety has priority."
            )
        elif name == "ventilation":
            st.write(
                f"**Humidity:** {data['humidity']:.1f}%  •  "
                f"**Air:** {data['air_temperature']:.1f}°C"
            )
            st.write(
                "Ventilation opens when humidity reaches 90% or when air temperature reaches the configured heat threshold."
            )
        elif name == "aeration":
            st.write(
                f"**DO:** {data['dissolved_oxygen']:.1f} mg/L  •  "
                f"**Water:** {data['water_temperature']:.1f}°C"
            )
            st.write(
                "Aeration protects fish oxygen availability. This function is intentionally prioritized over energy optimization."
            )
        elif name == "grid":
            st.write(
                f"**Battery:** {data['battery_soc']:.0f}%  •  "
                f"**Solar:** {data['solar_power']:.2f} kW"
            )
            st.write(
                "Grid support is used as a backup when solar generation is insufficient or battery reserve becomes low."
            )


# ============================================================
# AI DECISION ENGINE
# ============================================================
st.markdown('<div class="section-title"><span></span>AI Decision Engine</div>', unsafe_allow_html=True)

decisions = st.session_state.engine.analyze(data, weather)

for idx, decision in enumerate(decisions[:6]):
    css = priority_class(decision.priority)
    icon = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "NORMAL": "🟢",
        "OPTIMAL": "🔵",
        "INFO": "⚪",
    }.get(decision.priority, "⚪")

    with st.expander(
        f"{icon}  {decision.title}  ·  {decision.priority}",
        expanded=(idx == 0),
    ):
        st.markdown(f"**Condition:** {decision.condition}")
        st.markdown(f"**Decision:** {decision.action}")
        st.markdown(f"**Reason:** {decision.reason}")


# ============================================================
# PREDICTION
# ============================================================
st.markdown('<div class="section-title"><span></span>Prediction</div>', unsafe_allow_html=True)

p1, p2, p3, p4 = st.columns(4)

prediction_cards = [
    (
        p1,
        "Water Demand",
        f"{prediction['six_hour_water_demand_l']:.1f} L",
        "Expected demand over the next 6 hours",
    ),
    (
        p2,
        "Predicted Tank Level",
        f"{prediction['predicted_level_6h']:.0f}%",
        prediction["water_forecast"],
    ),
    (
        p3,
        "Thermal Risk",
        prediction["thermal_risk"],
        "Based on current + forecast thermal load",
    ),
    (
        p4,
        "Solar Outlook",
        prediction["solar_outlook"],
        "Based on current PV + weather conditions",
    ),
]

for col, label, value, note in prediction_cards:
    with col:
        st.markdown(
            f"""
            <div class="prediction-card">
                <div class="prediction-label">{label}</div>
                <div class="prediction-value">{value}</div>
                <div class="prediction-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    f"""
    <div class="info-box" style="margin-top:12px;">
        💧 <b>Water Forecast:</b> {prediction["water_forecast"]}.
        Estimated time to reach the 35% reserve threshold:
        <b>{prediction["hours_to_35_percent"]:.1f} hours</b>.
        This is a physics-inspired prototype prediction, not a trained ML model.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TIMELINE
# ============================================================
st.markdown('<div class="section-title"><span></span>AI Decision Timeline</div>', unsafe_allow_html=True)

if st.session_state.timeline:
    for item in st.session_state.timeline[:10]:
        icon = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "NORMAL": "🟢",
            "OPTIMAL": "🔵",
            "INFO": "⚪",
        }.get(item["priority"], "⚪")

        st.markdown(
            f"""
            <div class="timeline-item">
                <div class="timeline-time">{item["time"]}</div>
                <div>
                    <div class="timeline-title">{icon} {item["title"]}</div>
                    <div class="timeline-detail">{item["condition"]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No decisions recorded yet. Generate the next sensor reading to build the timeline.")


# ============================================================
# SAVINGS
# ============================================================
st.markdown('<div class="section-title"><span></span>Resource Savings</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

with s1:
    st.metric(
        "⚡ Energy Saved",
        f"{saved_pct:.1f}%",
        f"{max(0, st.session_state.energy_baseline_kwh - st.session_state.energy_actual_kwh):.3f} kWh",
    )

with s2:
    st.metric(
        "💧 Water Managed",
        f"{st.session_state.water_managed_l:.1f} L",
        "circulated by controlled pump operation",
    )

with s3:
    st.metric(
        "🔄 Simulation Cycles",
        str(st.session_state.cycle_count),
        "40-second simulated intervals",
    )


# ============================================================
# TRENDS
# ============================================================
if len(st.session_state.history) >= 2:
    st.markdown('<div class="section-title"><span></span>Farm Trends</div>', unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.history).set_index("Time")

    t1, t2 = st.columns(2)

    with t1:
        st.caption("Temperature")
        st.line_chart(df[["Air °C", "Water °C"]], height=220)

    with t2:
        st.caption("Water & Energy")
        st.line_chart(df[["Water Level %", "Battery %"]], height=220)


# ============================================================
# FOOTER
# ============================================================
last = (
    st.session_state.last_update.strftime("%H:%M:%S")
    if st.session_state.last_update
    else "--:--:--"
)

st.markdown(
    f"""
    <div class="footer-note">
        Last sensor update: {last} &nbsp;•&nbsp;
        Location: {weather["location"]} &nbsp;•&nbsp;
        Scenario: {data.get("scenario", "Normal")} &nbsp;•&nbsp;
        AI Resource Optimizer
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIMPLE STREAMLIT-ONLY LIVE LOOP
# No streamlit_autorefresh dependency.
# ============================================================
if st.session_state.live_mode:
    time.sleep(40)
    run_cycle()
    st.rerun()
