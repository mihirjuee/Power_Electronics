# =========================================================
# UPDATED SINGLE PHASE BRIDGE RECTIFIER SIMULATOR
# WITH LIVE CONDUCTION VISUALIZATION
# STREAMLIT + SCHEMDRAW
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
from matplotlib.patches import FancyArrowPatch
import schemdraw
import schemdraw.elements as elm

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Bridge Rectifier Conduction Visualizer",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("⚡ Single Phase Bridge Rectifier")
st.subheader("Live Diode Conduction Visualizer")

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.header("Controls")

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
# SIGNALS
# =========================================================

t = np.linspace(0, 0.04, 1000)

vin = Vm * np.sin(2*np.pi*freq*t)

vout = np.abs(vin)

instant_v = vin[time_index]

# =========================================================
# DETERMINE CONDUCTION
# =========================================================

if instant_v >= 0:

    cycle = "POSITIVE HALF CYCLE"

    conducting = "D1 and D3 Conducting"

    D1 = 'lime'
    D2 = 'gray'
    D3 = 'lime'
    D4 = 'gray'

    flow_color = 'lime'

else:

    cycle = "NEGATIVE HALF CYCLE"

    conducting = "D2 and D4 Conducting"

    D1 = 'gray'
    D2 = 'lime'
    D3 = 'gray'
    D4 = 'lime'

    flow_color = 'orange'

# =========================================================
# LAYOUT
# =========================================================

col1, col2 = st.columns([1,1])

# =========================================================
# LEFT : CIRCUIT VISUALIZATION
# =========================================================

with col1:

    st.subheader("Circuit Conduction Path")

    fig, ax = plt.subplots(figsize=(8,8))

    ax.set_xlim(-6,6)
    ax.set_ylim(-6,6)

    ax.axis('off')

    # -----------------------------------------------------
    # SOURCE
    # -----------------------------------------------------

    source = plt.Circle(
        (-4,0),
        0.7,
        fill=False,
        linewidth=3
    )

    ax.add_patch(source)

    ax.text(
        -4,
        0,
        "~",
        fontsize=28,
        ha='center',
        va='center'
    )

    # -----------------------------------------------------
    # CIRCUIT WIRES
    # -----------------------------------------------------

    ax.plot([-3.3,-1],[0,3],
            color='black',
            linewidth=3)

    ax.plot([-3.3,-1],[0,-3],
            color='black',
            linewidth=3)

    ax.plot([1,4],[3,3],
            color='black',
            linewidth=3)

    ax.plot([1,4],[-3,-3],
            color='black',
            linewidth=3)

    ax.plot([4,4],[3,-3],
            color='black',
            linewidth=3)

    # -----------------------------------------------------
    # LOAD RESISTOR
    # -----------------------------------------------------

    ax.plot([4.2,4.2],
            [2,-2],
            color='brown',
            linewidth=7)

    ax.text(
        4.6,
        0,
        "RL",
        fontsize=18,
        fontweight='bold'
    )

    # -----------------------------------------------------
    # DIODES
    # -----------------------------------------------------

    diodes = [
        (-1,3,'D1',D1),
        (1,3,'D2',D2),
        (-1,-3,'D3',D3),
        (1,-3,'D4',D4)
    ]

    for x,y,name,color in diodes:

        diode = plt.Circle(
            (x,y),
            0.45,
            fill=False,
            linewidth=5,
            edgecolor=color
        )

        ax.add_patch(diode)

        ax.text(
            x,
            y,
            name,
            fontsize=12,
            color=color,
            ha='center',
            va='center',
            fontweight='bold'
        )

    # =====================================================
    # LIVE CURRENT FLOW VISUALIZATION
    # =====================================================

    if instant_v >= 0:

        # SOURCE → D1
        ax.arrow(
            -3.1,0.4,
            1.3,1.9,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        # D1 → LOAD
        ax.arrow(
            -0.5,3,
            3.5,0,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        # LOAD → D3
        ax.arrow(
            4,-2.5,
            -3.3,-0.5,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        # D3 → SOURCE
        ax.arrow(
            -1.5,-2.8,
            -1.7,2.3,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

    else:

        # SOURCE → D2
        ax.arrow(
            -3.1,-0.4,
            3.3,3,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        # D2 → LOAD
        ax.arrow(
            1.5,3,
            2,0,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        # LOAD → D4
        ax.arrow(
            4,-2.5,
            -2.5,-0.2,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        # D4 → SOURCE
        ax.arrow(
            0.5,-3,
            -3.2,2.5,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

    # =====================================================
    # STATUS TEXT
    # =====================================================

    ax.text(
        -5.5,
        5,
        cycle,
        fontsize=15,
        color=flow_color,
        fontweight='bold'
    )

    ax.text(
        -5.5,
        4,
        conducting,
        fontsize=14,
        color=flow_color,
        fontweight='bold'
    )

    st.pyplot(fig)

# =========================================================
# RIGHT : WAVEFORMS
# =========================================================

with col2:

    st.subheader("Waveforms")

    fig2, ax2 = plt.subplots(figsize=(10,5))

    # Input waveform
    ax2.plot(
        t,
        vin,
        linewidth=3,
        color='red',
        label='Input AC Voltage'
    )

    # Output waveform
    ax2.plot(
        t,
        vout,
        linewidth=3,
        color='lime',
        label='Rectified Output'
    )

    # Markers
    ax2.plot(
        t[time_index],
        vin[time_index],
        'o',
        markersize=10,
        color='red'
    )

    ax2.plot(
        t[time_index],
        vout[time_index],
        'o',
        markersize=10,
        color='lime'
    )

    # Cursor
    ax2.axvline(
        t[time_index],
        linestyle='--',
        linewidth=2,
        color='blue'
    )

    ax2.grid(True)

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Voltage")

    ax2.legend()

    st.pyplot(fig2)

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
    "Instantaneous AC Voltage",
    f"{instant_v:.2f} V"
)

c3.metric(
    "RMS Input Voltage",
    f"{Vrms:.2f} V"
)

# =========================================================
# THEORY
# =========================================================

st.subheader("Theory")

st.latex(r"V_{DC} = \frac{2V_m}{\pi}")

st.latex(r"V_o = |V_m\sin(\omega t)|")

st.markdown("""
### Conduction Logic

#### Positive Half Cycle
- D1 and D3 conduct
- Current flows through load in one direction

#### Negative Half Cycle
- D2 and D4 conduct
- Load current direction remains same

Thus the output becomes pulsating DC.
""")
