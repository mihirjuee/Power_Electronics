# =========================================================
# SINGLE PHASE BRIDGE RECTIFIER SIMULATOR
# WORKING VERSION WITH:
# ✔ VISIBLE CIRCUIT DIAGRAM
# ✔ PLAY/PAUSE BUTTON
# ✔ AUTO ANIMATION
# ✔ DIODE CONDUCTION VISUALIZATION
# ✔ STREAMLIT
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
# pip install streamlit-autorefresh

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

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

# =========================================================
# SESSION STATE
# =========================================================

if "running" not in st.session_state:
    st.session_state.running = False

if "frame" not in st.session_state:
    st.session_state.frame = 0

# =========================================================
# PLAY / PAUSE BUTTONS
# =========================================================

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("▶ PLAY"):
        st.session_state.running = True

with col_btn2:
    if st.button("⏸ PAUSE"):
        st.session_state.running = False

# =========================================================
# AUTO REFRESH FOR ANIMATION
# =========================================================

if st.session_state.running:
    st_autorefresh(interval=50, key="animation")

    st.session_state.frame += 5

# =========================================================
# PARAMETERS
# =========================================================

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

# =========================================================
# TIME AXIS
# =========================================================

t = np.linspace(0, 0.04, 1000)

frame = st.session_state.frame % len(t)

# =========================================================
# WAVEFORMS
# =========================================================

vin = Vm * np.sin(2*np.pi*freq*t)

vout = np.abs(vin)

instant_v = vin[frame]

# =========================================================
# DIODE CONDUCTION
# =========================================================

if instant_v >= 0:

    D1 = 'lime'
    D2 = 'gray'
    D3 = 'lime'
    D4 = 'gray'

    conduction = "D1 & D3 Conducting"

    flow_color = 'lime'

else:

    D1 = 'gray'
    D2 = 'lime'
    D3 = 'gray'
    D4 = 'lime'

    conduction = "D2 & D4 Conducting"

    flow_color = 'orange'

# =========================================================
# LAYOUT
# =========================================================

col1, col2 = st.columns([1,1])

# =========================================================
# LEFT PANEL : CIRCUIT DIAGRAM
# =========================================================

with col1:

    st.subheader("Circuit Diagram")

    fig1, ax1 = plt.subplots(figsize=(7,7))

    ax1.set_xlim(-6,6)
    ax1.set_ylim(-6,6)

    ax1.axis('off')

    # -----------------------------------------------------
    # AC SOURCE
    # -----------------------------------------------------

    source = plt.Circle(
        (-4,0),
        0.7,
        fill=False,
        linewidth=3,
        color='black'
    )

    ax1.add_patch(source)

    ax1.text(
        -4,
        0,
        "~",
        fontsize=30,
        ha='center',
        va='center'
    )

    # -----------------------------------------------------
    # CIRCUIT WIRES
    # -----------------------------------------------------

    ax1.plot([-3.3,-1],[0,3],
             color='black',
             linewidth=3)

    ax1.plot([-3.3,-1],[0,-3],
             color='black',
             linewidth=3)

    ax1.plot([1,4],[3,3],
             color='black',
             linewidth=3)

    ax1.plot([1,4],[-3,-3],
             color='black',
             linewidth=3)

    ax1.plot([4,4],[3,-3],
             color='black',
             linewidth=3)

    # -----------------------------------------------------
    # LOAD RESISTOR
    # -----------------------------------------------------

    ax1.plot([4.2,4.2],
             [2,-2],
             color='brown',
             linewidth=7)

    ax1.text(
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

        ax1.add_patch(diode)

        ax1.text(
            x,
            y,
            name,
            fontsize=12,
            color=color,
            ha='center',
            va='center',
            fontweight='bold'
        )

    # -----------------------------------------------------
    # CURRENT FLOW VISUALIZATION
    # -----------------------------------------------------

    if instant_v >= 0:

        # Positive Half Cycle

        ax1.arrow(
            -3.1,0.5,
            1.5,2,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        ax1.arrow(
            -0.3,3,
            3.2,0,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        ax1.arrow(
            4,-2.2,
            -3.2,-0.4,
            color='lime',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

    else:

        # Negative Half Cycle

        ax1.arrow(
            -3.1,-0.5,
            3.2,3,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        ax1.arrow(
            1.3,3,
            2.1,0,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

        ax1.arrow(
            4,-2.2,
            -2.4,-0.2,
            color='orange',
            width=0.05,
            head_width=0.25,
            length_includes_head=True
        )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    ax1.text(
        -5.5,
        5,
        conduction,
        fontsize=15,
        color=flow_color,
        fontweight='bold'
    )

    st.pyplot(fig1)

# =========================================================
# RIGHT PANEL : WAVEFORMS
# =========================================================

with col2:

    st.subheader("Waveforms")

    fig2, ax2 = plt.subplots(figsize=(9,5))

    # Input waveform
    ax2.plot(
        t,
        vin,
        color='red',
        linewidth=3,
        label='Input AC'
    )

    # Output waveform
    ax2.plot(
        t,
        vout,
        color='lime',
        linewidth=3,
        label='Rectified Output'
    )

    # Moving markers
    ax2.plot(
        t[frame],
        vin[frame],
        'o',
        color='red',
        markersize=10
    )

    ax2.plot(
        t[frame],
        vout[frame],
        'o',
        color='lime',
        markersize=10
    )

    # Cursor line
    ax2.axvline(
        t[frame],
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
    "Instantaneous Voltage",
    f"{instant_v:.2f} V"
)

c3.metric(
    "RMS Voltage",
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

#### Negative Half Cycle
- D2 and D4 conduct

The load current always remains in the same direction,
thus producing pulsating DC.
""")
