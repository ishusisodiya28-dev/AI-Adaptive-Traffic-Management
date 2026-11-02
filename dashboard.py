
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="AI Traffic Management System",
    page_icon="🚦",
    layout="wide"
)

RESULTS = Path("results")

st.title("🚦 AI-Based Adaptive Traffic Management System")
st.caption("Fixed-Time vs Adaptive V2 vs PPO | SUMO Simulation")

# Load actual CSV results
try:
    comparison = pd.read_csv(RESULTS / "system_comparison.csv")
    co2 = pd.read_csv(RESULTS / "co2_comparison.csv")
except FileNotFoundError as e:
    st.error(f"Required result file missing: {e}")
    st.stop()

# Validate and prepare comparison data
required_columns = ["Metric", "Fixed-Time", "Adaptive V2", "PPO"]

if not all(col in comparison.columns for col in required_columns):
    st.error("system_comparison.csv ka format expected format se match nahi karta.")
    st.stop()

comparison = comparison.set_index("Metric")

systems = ["Fixed-Time", "Adaptive V2", "PPO"]

if not {"System", "Total_CO2_kg", "Vehicles"}.issubset(co2.columns):
    st.error("co2_comparison.csv ka format expected format se match nahi karta.")
    st.stop()

co2_values = co2.set_index("System")["Total_CO2_kg"]

if not all(system in co2_values.index for system in systems):
    st.error("CO2 CSV mein teeno systems ka data available nahi hai.")
    st.stop()

# Header metrics
st.subheader("📊 System Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Control Methods", "3")
c2.metric("Vehicles Simulated", "450")
c3.metric("Traffic Signal", "B1")

st.divider()

# CO2 metrics
st.subheader("🌍 CO₂ Emission Results")

cols = st.columns(3)

for col, system in zip(cols, systems):
    value = float(co2_values[system])
    col.metric(system, f"{value:.2f} kg")

st.caption(
    "CO₂ reduction compared with Fixed-Time is calculated from "
    "the actual SUMO emission comparison."
)

st.divider()

# Metric selection
st.subheader("📈 Performance Comparison")

metric_options = [
    "Speed (m/s)",
    "Duration (s)",
    "Waiting Time (s)",
    "Time Loss (s)",
    "Depart Delay (s)",
    "CO₂ Emissions (kg)"
]

selected_metric = st.selectbox(
    "Select metric",
    metric_options
)

if selected_metric == "CO₂ Emissions (kg)":
    values = [float(co2_values[s]) for s in systems]
else:
    if selected_metric not in comparison.index:
        st.warning("Selected metric CSV mein available nahi hai.")
        st.stop()

    values = [
        float(comparison.loc[selected_metric, system])
        for system in systems
    ]

fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.bar(systems, values)

ax.set_title(selected_metric + " — System Comparison")
ax.set_ylabel(selected_metric)
ax.grid(axis="y", alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.2f}",
        ha="center",
        va="bottom"
    )

st.pyplot(fig)
plt.close(fig)

st.divider()

# Complete comparison table
st.subheader("📋 Complete Performance Results")

table = comparison.copy()
table.loc["CO₂ Emissions (kg)"] = [
    float(co2_values[s]) for s in systems
]

st.dataframe(
    table.round(2),
    use_container_width=True
)

st.divider()

# CO2 reduction
fixed_co2 = float(co2_values["Fixed-Time"])

st.subheader("♻️ CO₂ Reduction vs Fixed-Time")

for system in ["Adaptive V2", "PPO"]:
    reduction = (
        (fixed_co2 - float(co2_values[system]))
        / fixed_co2
    ) * 100

    st.write(f"**{system}: {reduction:.2f}% reduction**")

st.divider()

st.subheader("⚙️ System Workflow")

a, b, c, d = st.columns(4)

a.info("📹 Traffic Input\n\nCamera / SUMO")
b.info("🚗 Vehicle Analysis\n\nVehicle and queue data")
c.info("🧠 AI Decision\n\nAdaptive + PPO")
d.info("🚦 Signal Control\n\nDynamic green timing")

st.success("Dashboard loaded using actual CSV simulation results.")

st.caption(
    "Technology: Python | SUMO | TraCI | PPO | Streamlit"
)
