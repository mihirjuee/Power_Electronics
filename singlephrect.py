# =========================================================
# UPDATED BRIDGE RECTIFIER SIMULATOR
# USING PREVIOUS CLEAN CIRCUIT DIAGRAM
# + LIVE CONDUCTION VISUALIZATION
# STREAMLIT APP
# =========================================================

# RUN:
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
import schemdraw
import schemdraw.elements as elm

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Bridge Rectifier Visualizer",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("⚡ Single Phase Bridge Rectifier")

st.markdown("""
Interactive visualization of:
- Full Wave Bridge Rectifier
- Diode Conduction
- Current Flow
- Input & Output Waveforms
""")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Controls")

Vm = st.sidebar.slider(
    "Peak Voltage",
    50,
    400,
    230
)

freq = st.sidebar.slider(
    "Frequency",
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
# SIGNALS
# =========================================================

t = np.linspace(0, 0.04, 1000)

vin = Vm * np.sin(2*np.pi*freq*t)

vout = np.abs(vin)

instant_v = vin[time_index]

# =========================================================
# DIODE CONDUCTION
# =========================================================

if instant_v >= 0:

    D1_color = 'lime'
    D2_color = 'gray'
    D3_color = 'lime'
    D4_color = 'gray'

    conduction_text = "Positive Half Cycle → D1 & D3 Conduct"

    flow_color = 'lime'

else:

    D1_color = 'gray'
    D2_color = 'lime'
    D3_color = 'gray'
    D4_color = 'lime'

    conduction_text = "Negative Half Cycle → D2 & D4 Conduct"

    flow_color = 'orange'

# =========================================================
# CIRCUIT DIAGRAM
# =========================================================

st.subheader("Bridge Rectifier Circuit")

with schemdraw.Drawing(show=False) as d:

    d.config(unit=2.5)

    # -----------------------------------------------------
    # AC SOURCE
    # -----------------------------------------------------

    d += elm.SourceSin().label('AC Input')

    d += elm.Line().right()

    # -----------------------------------------------------
    # TOP LEFT DIODE D1
    # -----------------------------------------------------

    d.push()

    d1 = d += elm.Diode().up().color(D1_color).label('D1')

    d += elm.Line().right(2)

    # -----------------------------------------------------
    # LOAD RESISTOR
    # -----------------------------------------------------

    d += elm.Resistor().down().label('RL')

    # -----------------------------------------------------
    # BOTTOM RIGHT DIODE D3
    # -----------------------------------------------------

    d += elm.Diode().down().color(D3_color).label('D3')

    d += elm.Line().left(2)

    d.pop()

    # -----------------------------------------------------
    # LOWER BRANCH
    # -----------------------------------------------------

    d += elm.Line().down(4)

    d.push()

    # -----------------------------------------------------
    # D4
    # -----------------------------------------------------

    d += elm.Diode().right().color(D4_color).label('D4')

    d += elm.Line().up(4)

    d.pop()

    # -----------------------------------------------------
    # D2
    # -----------------------------------------------------

    d.move(dx=0, dy=4)

    d += elm.Diode().right().color(D2_color).label('D2')

    # -----------------------------------------------------
    # OUTPUT TERMINALS
    # -----------------------------------------------------

    d += elm.Dot().label('+Vo')

    d.move(dx=0, dy=-4)

    d += elm.Dot().label('-Vo')

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    st.pyplot(d.fig)

# =========================================================
# CONDUCTION STATUS
# =========================================================

st.subheader("Live Conduction Status")

st.markdown(
    f"""
    <h2 style='color:{flow_color};'>
    {conduction_text}
    </h2>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CURRENT PATH EXPLANATION
# =========================================================

if instant_v >= 0:

    st.success("""
    Current Path:
    AC Source → D1 → Load → D3 → Source
    """)

else:

    st.warning("""
    Current Path:
    AC Source → D2 → Load → D4 → Source
    """)

# =========================================================
# WAVEFORMS
# =========================================================

st.subheader("Waveforms")

fig, ax = plt.subplots(figsize=(12,5))

# Input waveform
ax.plot(
    t,
    vin,
    color='red',
    linewidth=3,
    label='Input AC Voltage'
)

# Output waveform
ax.plot(
    t,
    vout,
    color='lime',
    linewidth=3,
    label='Rectified Output'
)

# Current time markers
ax.plot(
    t[time_index],
    vin[time_index],
    'o',
    color='red',
    markersize=10
)

ax.plot(
    t[time_index],
    vout[time_index],
    'o',
    color='lime',
    markersize=10
)

# Cursor line
ax.axvline(
    t[time_index],
    linestyle='--',
    linewidth=2,
    color='blue'
)

# Grid
ax.grid(True)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage")

ax.set_title("AC Input & Rectified Output")

ax.legend()

st.pyplot(fig)

# =========================================================
# METRICS
# =========================================================

st.subheader("Output Parameters")

Vdc = 2*Vm/np.pi
Vrms = Vm/np.sqrt(2)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Average DC Voltage",
    f"{Vdc:.2f} V"
)

c2.metric(
    "RMS Input Voltage",
    f"{Vrms:.2f} V"
)

c3.metric(
    "Instantaneous Input",
    f"{instant_v:.2f} V"
)

# =========================================================
# THEORY
# =========================================================

st.subheader("Theory")

st.latex(
    r"V_{DC} = \frac{2V_m}{\pi}"
)

st.latex(
    r"V_o = |V_m \sin(\omega t)|"
)

st.markdown("""
### Bridge Rectifier Working

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
    "⚡ Educational Power Electronics Simulator"
)
