# =========================================================
# SINGLE PHASE BRIDGE RECTIFIER
# SCHEMDRAW CONDUCTION VISUALIZER
# COMPLETE STREAMLIT APP
# =========================================================

# RUN USING:
# streamlit run app.py

# =========================================================
# INSTALL REQUIRED LIBRARIES
# =========================================================

# pip install streamlit
# pip install schemdraw
# pip install numpy
# pip install matplotlib

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
- Current Flow
- Input & Output Waveforms
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

frame = st.sidebar.slider(
    "Animation Frame",
    0,
    999,
    100
)

# =========================================================
# TIME VECTOR
# =========================================================

t = np.linspace(0, 0.04, 1000)

# =========================================================
# INPUT & OUTPUT VOLTAGES
# =========================================================

vin = Vm * np.sin(2*np.pi*freq*t)

vout = np.abs(vin)

instant_v = vin[frame]

# =========================================================
# DIODE CONDUCTION LOGIC
# =========================================================

if instant_v >= 0:

    D1_color = 'lime'
    D2_color = 'gray'
    D3_color = 'lime'
    D4_color = 'gray'

    conduction_text = "Positive Half Cycle → D1 & D3 Conduct"

    path_text = "AC Source → D1 → Load → D3 → Source"

    status_color = "green"

else:

    D1_color = 'gray'
    D2_color = 'lime'
    D3_color = 'gray'
    D4_color = 'lime'

    conduction_text = "Negative Half Cycle → D2 & D4 Conduct"

    path_text = "AC Source → D2 → Load → D4 → Source"

    status_color = "orange"

# =========================================================
# MAIN LAYOUT
# =========================================================

col1, col2 = st.columns([1,1])

# =========================================================
# LEFT SIDE : CIRCUIT DIAGRAM
# =========================================================

with col1:

    st.subheader("Bridge Rectifier Circuit")

    # =====================================================
    # SCHEMDRAW CIRCUIT
    # =====================================================

    with schemdraw.Drawing(show=False) as d:

        d.config(unit=2.5)

        # -------------------------------------------------
        # AC SOURCE
        # -------------------------------------------------

        d += elm.SourceSin().label('AC Input')

        d += elm.Line().right()

        # Save node
        d.push()

        # =================================================
        # TOP PATH
        # =================================================

        # D1
        diode1 = elm.Diode().up().color(D1_color).label('D1')
        d += diode1

        d += elm.Line().right(2)

        # Load
        d += elm.Resistor().down().label('RL')

        # D3
        diode3 = elm.Diode().down().color(D3_color).label('D3')
        d += diode3

        d += elm.Line().left(2)

        d.pop()

        # =================================================
        # LOWER PATH
        # =================================================

        d += elm.Line().down(4)

        d.push()

        # D4
        diode4 = elm.Diode().right().color(D4_color).label('D4')
        d += diode4

        d += elm.Line().up(4)

        d.pop()

        # =================================================
        # D2
        # =================================================

        d.move(dx=0, dy=4)

        diode2 = elm.Diode().right().color(D2_color).label('D2')
        d += diode2

        # =================================================
        # OUTPUT TERMINALS
        # =================================================

        d += elm.Dot().label('+Vo')

        d.move(dx=0, dy=-4)

        d += elm.Dot().label('-Vo')

        # =================================================
        # DISPLAY CIRCUIT
        # =================================================

        st.pyplot(d.fig)

    # =====================================================
    # CONDUCTION STATUS
    # =====================================================

    st.markdown(
        f"""
        <h3 style='color:{status_color};'>
        {conduction_text}
        </h3>
        """,
        unsafe_allow_html=True
    )

    st.info(path_text)

# =========================================================
# RIGHT SIDE : WAVEFORMS
# =========================================================

with col2:

    st.subheader("Input & Output Waveforms")

    fig, ax = plt.subplots(figsize=(10,5))

    # -----------------------------------------------------
    # INPUT WAVEFORM
    # -----------------------------------------------------

    ax.plot(
        t,
        vin,
        color='red',
        linewidth=3,
        label='Input AC Voltage'
    )

    # -----------------------------------------------------
    # OUTPUT WAVEFORM
    # -----------------------------------------------------

    ax.plot(
        t,
        vout,
        color='lime',
        linewidth=3,
        label='Rectified Output'
    )

    # -----------------------------------------------------
    # MOVING POINTS
    # -----------------------------------------------------

    ax.plot(
        t[frame],
        vin[frame],
        'o',
        color='red',
        markersize=10
    )

    ax.plot(
        t[frame],
        vout[frame],
        'o',
        color='lime',
        markersize=10
    )

    # -----------------------------------------------------
    # CURSOR LINE
    # -----------------------------------------------------

    ax.axvline(
        t[frame],
        linestyle='--',
        linewidth=2,
        color='blue'
    )

    # -----------------------------------------------------
    # AXIS SETTINGS
    # -----------------------------------------------------

    ax.grid(True)

    ax.set_xlabel("Time (s)")

    ax.set_ylabel("Voltage (V)")

    ax.set_title("AC Input & Full Wave Rectified Output")

    ax.legend()

    # -----------------------------------------------------
    # DISPLAY PLOT
    # -----------------------------------------------------

    st.pyplot(fig)

# =========================================================
# OUTPUT PARAMETERS
# =========================================================

st.subheader("Output Parameters")

Vdc = 2 * Vm / np.pi

Vrms = Vm / np.sqrt(2)

colA, colB, colC = st.columns(3)

colA.metric(
    "Average DC Voltage",
    f"{Vdc:.2f} V"
)

colB.metric(
    "RMS Input Voltage",
    f"{Vrms:.2f} V"
)

colC.metric(
    "Instantaneous Voltage",
    f"{instant_v:.2f} V"
)

# =========================================================
# THEORY
# =========================================================

st.subheader("Theory")

st.latex(r"V_{DC} = \frac{2V_m}{\pi}")

st.latex(r"V_o = |V_m \sin(\omega t)|")

st.markdown("""
### Working Principle

#### Positive Half Cycle
- D1 and D3 are forward biased
- D2 and D4 are reverse biased
- Current flows through load in one direction

#### Negative Half Cycle
- D2 and D4 are forward biased
- D1 and D3 are reverse biased
- Load current direction remains same

Thus the bridge rectifier converts AC into pulsating DC.
""")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("⚡ Power Electronics Educational Simulator")
