# =========================================================
# STREAMLIT + SCHEMDRAW
# SINGLE PHASE BRIDGE RECTIFIER SIMULATOR
# =========================================================

# RUN USING:
# streamlit run app.py

# =========================================================
# INSTALL REQUIRED LIBRARIES
# =========================================================

# pip install streamlit
# pip install matplotlib
# pip install numpy
# pip install schemdraw

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import schemdraw
import schemdraw.elements as elm

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Bridge Rectifier Simulator",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("⚡ Single Phase Bridge Rectifier Simulator")

st.markdown("""
Interactive visualization of:
- Bridge Rectifier Circuit
- Diode Conduction
- AC to DC Conversion
- Full Wave Rectification
""")

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.header("Simulation Controls")

Vm = st.sidebar.slider(
    "Peak Voltage (Vm)",
    50,
    400,
    230
)

freq = st.sidebar.slider(
    "Frequency (Hz)",
    1,
    100,
    50
)

time_index = st.sidebar.slider(
    "Time Position",
    0,
    999,
    100
)

# =========================================================
# TIME AXIS
# =========================================================

t = np.linspace(0, 0.04, 1000)

# =========================================================
# INPUT & OUTPUT VOLTAGES
# =========================================================

vin = Vm * np.sin(2*np.pi*freq*t)

vout = np.abs(vin)

current_v = vin[time_index]

# =========================================================
# DIODE CONDUCTION LOGIC
# =========================================================

if current_v >= 0:

    conducting = "D1 & D3 Conducting"

    D1_color = 'lime'
    D2_color = 'gray'
    D3_color = 'lime'
    D4_color = 'gray'

else:

    conducting = "D2 & D4 Conducting"

    D1_color = 'gray'
    D2_color = 'lime'
    D3_color = 'gray'
    D4_color = 'lime'

# =========================================================
# SCHEMDRAW CIRCUIT
# =========================================================

st.subheader("Bridge Rectifier Circuit Diagram")

with schemdraw.Drawing(show=False) as d:

    d.config(unit=2.5)

    # -----------------------------------------------------
    # AC SOURCE
    # -----------------------------------------------------

    source = d.add(
        elm.SourceSin().label('AC Input')
    )

    d.add(elm.Line().right())

    # -----------------------------------------------------
    # TOP LEFT NODE
    # -----------------------------------------------------

    d.push()

    # D1
    d1 = d.add(
        elm.Diode().up().color(D1_color).label('D1')
    )

    d.add(elm.Line().right(2))

    # LOAD
    d.add(
        elm.Resistor().down().label('RL')
    )

    # D3
    d.add(
        elm.Diode().down().color(D3_color).label('D3')
    )

    d.add(elm.Line().left(2))

    d.pop()

    # -----------------------------------------------------
    # LOWER BRANCH
    # -----------------------------------------------------

    d.add(elm.Line().down(4))

    d.push()

    # D4
    d.add(
        elm.Diode().right().color(D4_color).label('D4')
    )

    d.add(elm.Line().up(4))

    d.pop()

    # D2
    d.move(dx=0, dy=4)

    d.add(
        elm.Diode().right().color(D2_color).label('D2')
    )

    # -----------------------------------------------------
    # OUTPUT LABELS
    # -----------------------------------------------------

    d.add(elm.Dot().label('+Vo'))

    d.move(dx=0, dy=-4)

    d.add(elm.Dot().label('-Vo'))

    # -----------------------------------------------------
    # DISPLAY CIRCUIT
    # -----------------------------------------------------

    st.pyplot(d.fig)

# =========================================================
# WAVEFORM PLOT
# =========================================================

st.subheader("Waveforms")

fig, ax = plt.subplots(figsize=(12,5))

# Input waveform
ax.plot(
    t,
    vin,
    linewidth=3,
    color='red',
    label='Input AC Voltage'
)

# Output waveform
ax.plot(
    t,
    vout,
    linewidth=3,
    color='lime',
    label='Rectified Output'
)

# Current time marker
ax.plot(
    t[time_index],
    vin[time_index],
    'o',
    markersize=10,
    color='red'
)

ax.plot(
    t[time_index],
    vout[time_index],
    'o',
    markersize=10,
    color='lime'
)

# Cursor line
ax.axvline(
    t[time_index],
    linestyle='--',
    linewidth=2,
    color='blue'
)

# Axis settings
ax.grid(True)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage")

ax.set_title("Input AC & Rectified Output")

ax.legend()

st.pyplot(fig)

# =========================================================
# CONDUCTION STATUS
# =========================================================

st.subheader("Conduction Status")

if current_v >= 0:

    st.success(conducting)

else:

    st.warning(conducting)

# =========================================================
# METRICS
# =========================================================

Vdc = 2*Vm/np.pi

Vrms = Vm/np.sqrt(2)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average DC Voltage",
    f"{Vdc:.2f} V"
)

col2.metric(
    "RMS Input Voltage",
    f"{Vrms:.2f} V"
)

col3.metric(
    "Instantaneous Input",
    f"{current_v:.2f} V"
)

# =========================================================
# THEORY
# =========================================================

st.subheader("Theory")

st.latex(
    r"V_{DC} = \\frac{2V_m}{\\pi}"
)

st.latex(
    r"V_o = |V_m \\sin(\\omega t)|"
)

st.markdown("""
### Working Principle

#### Positive Half Cycle
- D1 and D3 conduct
- D2 and D4 remain OFF

#### Negative Half Cycle
- D2 and D4 conduct
- D1 and D3 remain OFF

The load current always flows in the same direction,
thus producing pulsating DC output.
""")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    "⚡ Educational Simulator for Power Electronics"
)
