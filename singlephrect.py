# =========================================================
# STREAMLIT APP
# SINGLE PHASE BRIDGE RECTIFIER SIMULATOR
# =========================================================

# Run using:
# streamlit run app.py

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

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
- Full wave bridge rectifier
- Diode conduction
- Input AC waveform
- Rectified DC waveform
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
# WAVEFORMS
# =========================================================

vin = Vm * np.sin(2*np.pi*freq*t)

vout = np.abs(vin)

# Current value
current_v = vin[time_index]

# =========================================================
# DETERMINE CONDUCTING DIODES
# =========================================================

OFF = 'gray'
ON = 'lime'

D1 = OFF
D2 = OFF
D3 = OFF
D4 = OFF

if current_v >= 0:

    D1 = ON
    D3 = ON

    conduction_text = "D1 & D3 Conducting"

    flow_color = 'lime'

else:

    D2 = ON
    D4 = ON

    conduction_text = "D2 & D4 Conducting"

    flow_color = 'orange'

# =========================================================
# CREATE FIGURE
# =========================================================

fig = plt.figure(figsize=(14,8))

# =========================================================
# CIRCUIT AXIS
# =========================================================

ax1 = plt.subplot(1,2,1)

ax1.set_xlim(-6,6)
ax1.set_ylim(-6,6)

ax1.set_aspect('equal')

ax1.axis('off')

ax1.set_title("Bridge Rectifier Circuit")

# =========================================================
# AC SOURCE
# =========================================================

source = Circle(
    (-4,0),
    0.7,
    edgecolor='black',
    facecolor='none',
    linewidth=3
)

ax1.add_patch(source)

ax1.text(
    -4,
    0,
    "~",
    fontsize=28,
    ha='center',
    va='center'
)

# =========================================================
# CIRCUIT WIRING
# =========================================================

ax1.plot([-3.3,-1],[0,3],
         color='black',
         linewidth=3)

ax1.plot([-3.3,-1],[0,-3],
         color='black',
         linewidth=3)

ax1.plot([1,4],[3,3],
         color='black',
         linewidth=3)

ax1.plot([1,-1],[-3,-3],
         color='black',
         linewidth=3)

ax1.plot([4,4],[3,-3],
         color='black',
         linewidth=3)

# =========================================================
# LOAD RESISTOR
# =========================================================

ax1.plot([4.2,4.2],
         [2,-2],
         color='brown',
         linewidth=6)

ax1.text(
    4.6,
    0,
    "RL",
    fontsize=18,
    fontweight='bold'
)

# =========================================================
# DIODE POSITIONS
# =========================================================

diodes = [
    (-1,3,'D1',D1),
    (1,3,'D2',D2),
    (-1,-3,'D3',D3),
    (1,-3,'D4',D4)
]

# =========================================================
# DRAW DIODES
# =========================================================

for x,y,label,color in diodes:

    diode = Circle(
        (x,y),
        0.4,
        edgecolor=color,
        facecolor='none',
        linewidth=4
    )

    ax1.add_patch(diode)

    ax1.text(
        x,
        y,
        label,
        fontsize=12,
        color=color,
        ha='center',
        va='center',
        fontweight='bold'
    )

# =========================================================
# CURRENT FLOW
# =========================================================

if current_v >= 0:

    ax1.arrow(
        -2.5,1,
        1,1.5,
        color='green',
        linewidth=3,
        width=0.03,
        head_width=0.2,
        length_includes_head=True
    )

    ax1.arrow(
        2.5,3,
        1.2,-1.5,
        color='green',
        linewidth=3,
        width=0.03,
        head_width=0.2,
        length_includes_head=True
    )

else:

    ax1.arrow(
        -2.5,-1,
        1,-1.5,
        color='orange',
        linewidth=3,
        width=0.03,
        head_width=0.2,
        length_includes_head=True
    )

    ax1.arrow(
        2.5,-3,
        1.2,1.5,
        color='orange',
        linewidth=3,
        width=0.03,
        head_width=0.2,
        length_includes_head=True
    )

# =========================================================
# STATUS TEXT
# =========================================================

ax1.text(
    -5,
    5,
    "AC INPUT",
    fontsize=16,
    fontweight='bold'
)

ax1.text(
    2.5,
    5,
    "DC OUTPUT",
    fontsize=16,
    color='green',
    fontweight='bold'
)

ax1.text(
    -5,
    -5,
    conduction_text,
    fontsize=15,
    color=flow_color,
    fontweight='bold'
)

# =========================================================
# WAVEFORM AXIS
# =========================================================

ax2 = plt.subplot(1,2,2)

ax2.set_title("Input & Output Waveforms")

ax2.plot(
    t,
    vin,
    linewidth=3,
    label='Input AC'
)

ax2.plot(
    t,
    vout,
    linewidth=3,
    label='Rectified Output'
)

# =========================================================
# MOVING MARKERS
# =========================================================

ax2.plot(
    t[time_index],
    vin[time_index],
    'o',
    markersize=10
)

ax2.plot(
    t[time_index],
    vout[time_index],
    'o',
    markersize=10
)

# =========================================================
# TIME CURSOR
# =========================================================

ax2.axvline(
    t[time_index],
    linestyle='--',
    linewidth=2
)

# =========================================================
# AXIS SETTINGS
# =========================================================

ax2.grid(True)

ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Voltage")

ax2.legend()

# =========================================================
# DISPLAY FIGURE
# =========================================================

st.pyplot(fig)

# =========================================================
# OUTPUT VALUES
# =========================================================

Vdc = 2*Vm/np.pi

Vrms = Vm/np.sqrt(2)

# =========================================================
# METRICS
# =========================================================

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
    "Instantaneous Voltage",
    f"{current_v:.2f} V"
)

# =========================================================
# THEORY SECTION
# =========================================================

st.subheader("Theory")

st.latex(r"V_{DC} = \\frac{2V_m}{\\pi}")

st.latex(r"V_o = |V_m \\sin(\\omega t)|")

st.write("""
During:
- Positive half cycle → D1 and D3 conduct
- Negative half cycle → D2 and D4 conduct

The load current always flows in the same direction,
producing pulsating DC output.
""")
