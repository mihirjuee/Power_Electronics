import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Buck Converter", layout="wide")
st.title("⚡ DC–DC Buck Converter Simulation")

st.latex(r"V_o = D \cdot V_{in}")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Parameters")

Vin = st.sidebar.number_input("Input Voltage (V)", value=12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 1.0, 0.5)
R = st.sidebar.number_input("Load Resistance (Ω)", value=10.0)
L = st.sidebar.number_input("Inductance (H)", value=1e-3, format="%.5f")
C = st.sidebar.number_input("Capacitance (F)", value=100e-6, format="%.6f")
fs = st.sidebar.number_input("Switching Frequency (Hz)", value=50000.0)

# ================= CIRCUIT DIAGRAM =================
st.subheader("🔌 Circuit Diagram")

with schemdraw.Drawing() as d:
    d += elm.SourceV().label('Vin')

    d += elm.Line().right()
    d += elm.Switch().label('S')

    d += elm.Line().right()
    d += elm.Inductor().label('L')

    d += elm.Line().right()
    d += elm.Dot()
    d.push()

    d += elm.Capacitor().down().label('C')
    d += elm.Ground()

    d.pop()
    d += elm.Line().right()

    d += elm.Resistor().down().label('R')
    d += elm.Ground()

    d += elm.Line().left(6)

    d += elm.Diode().down().at(d.elements[2].end).label('D')
    d += elm.Ground()

    st.pyplot(d.draw())

# ================= CALCULATIONS =================
T = 1 / fs
Vo = D * Vin
Io = Vo / R

t = np.linspace(0, T, 1000)

delta_I = (Vin - Vo) * D * T / L
IL = Io + (delta_I / 2) * np.sign(np.sin(2 * np.pi * fs * t))

delta_V = delta_I / (8 * fs * C)
Vo_wave = Vo + (delta_V / 2) * np.sin(2 * np.pi * fs * t)

# ================= RESULTS =================
st.subheader("📊 Results")

c1, c2, c3 = st.columns(3)
c1.metric("Output Voltage", f"{Vo:.2f} V")
c2.metric("Output Current", f"{Io:.2f} A")
c3.metric("Ripple Current", f"{delta_I:.4f} A")

# ================= PLOTS =================
st.subheader("📈 Waveforms")

fig, ax = plt.subplots(2, 1, figsize=(10, 6))

ax[0].plot(t * 1e6, IL)
ax[0].set_title("Inductor Current")
ax[0].set_xlabel("Time (µs)")
ax[0].grid()

ax[1].plot(t * 1e6, Vo_wave)
ax[1].set_title("Output Voltage Ripple")
ax[1].set_xlabel("Time (µs)")
ax[1].grid()

st.pyplot(fig)

# ================= THEORY =================
st.subheader("📘 Working")

st.write("""
- Switch ON → Inductor charges  
- Switch OFF → Inductor discharges via diode  
- Capacitor smooths output  
""")
