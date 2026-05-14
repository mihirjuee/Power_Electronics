# =========================================================
# SINGLE PHASE BRIDGE RECTIFIER VISUALIZER
# STREAMLIT + SCHEMDRAW
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
- AC to DC Conversion
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

instant_v = vin[time_index]

# =========================================================
# DIODE CONDUCTION LOGIC
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
    # SAVE STARTING POINT
    # -----------------------------------------------------

    start = d.here

    # =====================================================
    # TOP BRANCH
    # =====================================================

    d.push()

    # D1
    d1 = elm.Diode().up().color(D1_color).label('D1')
    d += d1

    d += elm.Line().right(2)

    # LOAD
    d += elm.Resistor().down().label('RL')

    # D3
    d3 = elm.Diode().down().color(D3_color).label('D3')
    d += d3

    d += elm.Line().left(2)

    d.pop()

    # =====================================================
    # LOWER BRANCH
    # =====================================================

    d += elm.Line().down(4)

    d.push()

    # D4
    d4 = elm.Diode().right().color(D4_color).label('D4')
    d += d4

    d += elm.Line().up(4)

    d.pop()

    # =====================================================
    # D2
    # =====================================================

    d.move(dx=0, dy=4)

    d2 = elm.Diode().right().color(D2_color).label('D2')
    d += d2

    # =====================================================
    # OUTPUT TERMINALS
    # =====================================================

    d += elm.Dot().label('+Vo')

    d.move(dx=0, dy=-4)

    d += elm.Dot().label('-Vo')

    # =====================================================
    # DISPLAY CIRCUIT
    # =====================================================

    st.pyplot(d.fig)

# =========================================================
# CONDUCTION STATUS
# =========================================================

st.subheader("Conduction Status")

st.markdown(
    f"""
    <h2 style='color:{flow_color};'>
    {conduction_text}
    </h2>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CURRENT PATH
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
# WAVEFORM PLOT
# =========================================================

st.subheader("Input & Output Waveforms")

fig, ax = plt.subplots(figsize=(12,5))

# ---------------------------------------------------------
# INPUT WAVEFORM
# ---------------------------------------------------------

ax.plot(
    t,
    vin,
    linewidth=3,
    color='red',
    label='Input AC Voltage'
)

# ---------------------------------------------------------
# OUTPUT WAVEFORM
# ---------------------------------------------------------

ax.plot(
    t,
    vout,
    linewidth=3,
    color='lime',
    label='Rectified Output'
)

# ---------------------------------------------------------
# MOVING MARKERS
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# CURSOR LINE
# ---------------------------------------------------------

ax.axvline(
    t[time_index],
    linestyle='--',
    linewidth=2,
    color='blue'
)

# ---------------------------------------------------------
# AXIS SETTINGS
# ---------------------------------------------------------

ax.grid(True)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage")

ax.set_title("AC Input & Full Wave Rectified Output")

ax.legend()

# ---------------------------------------------------------
# DISPLAY PLOT
# ---------------------------------------------------------

st.pyplot(fig)

# =========================================================
# OUTPUT PARAMETERS
# =========================================================

st.subheader("Output Parameters")

Vdc = 2 * Vm / np.pi

Vrms = Vm / np.sqrt(2)

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
    f"{instant_v:.2f} V"
)

# =========================================================
# THEORY SECTION
# =========================================================

st.subheader("Theory")

st.latex(
    r"V_{DC} = \frac{2V_m}{\pi}"
)

st.latex(
    r"V_o = |V_m \sin(\omega t)|"
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
therefore pulsating DC is obtained.
""")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("⚡ Educational Power Electronics Simulator")
