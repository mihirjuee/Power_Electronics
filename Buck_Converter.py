import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Buck Converter", layout="wide")
st.title("⚡ Buck Converter (Static Simulation)")

st.latex(r"V_o = D \cdot V_{in}")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Controls")

Vin = st.sidebar.number_input("Input Voltage (V)", 12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 1.0, 0.5)
fs = st.sidebar.number_input("Switching Frequency (Hz)", 20000.0)

R = st.sidebar.number_input("Load Resistance (Ω)", 10.0)
L = st.sidebar.number_input("Inductance (H)", 1e-3, format="%.5f")
C = st.sidebar.number_input("Capacitance (F)", 100e-6, format="%.6f")

# ================= TIME =================
T = 1 / fs
t = np.linspace(0, 5*T, 2000)

# ================= IDEAL OUTPUT =================
Vo = D * Vin
Io = Vo / R

# ================= INDUCTOR CURRENT =================
delta_IL = (Vin - Vo) * D * T / L

# Triangular current waveform
IL = Io + (delta_IL/2) * np.sign(np.sin(2*np.pi*fs*t))

# ================= CAPACITOR CURRENT =================
IC = IL - Io   # capacitor current = inductor - load

# ================= OUTPUT VOLTAGE RIPPLE =================
delta_Vo = delta_IL / (8 * fs * C)

Vo_wave = Vo + (delta_Vo/2) * np.sin(2*np.pi*fs*t)

# ================= CIRCUIT =================
st.subheader("🔌 Circuit Diagram")

def draw_circuit():
    with schemdraw.Drawing() as d:

        d += elm.SourceV().label('Vin')
        d += elm.Line().right()

        d += elm.NFet().label("MOSFET")

        d += elm.Line().right()

        d.push()

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

        d.pop()

        d += elm.Diode().down().label('D')
        d += elm.Ground()

        fig = d.draw()
        return fig.fig

st.pyplot(draw_circuit())

# ================= WAVEFORMS =================
st.subheader("📈 Waveforms")

fig, ax = plt.subplots(4, 1, figsize=(10, 10), sharex=True)

# Output Voltage
ax[0].plot(t*1e6, Vo_wave)
ax[0].set_title("Output Voltage (Vo)")
ax[0].set_ylabel("Voltage (V)")
ax[0].grid()

# Inductor Current
ax[1].plot(t*1e6, IL)
ax[1].set_title("Inductor Current (iL)")
ax[1].set_ylabel("Current (A)")
ax[1].grid()

# Capacitor Current
ax[2].plot(t*1e6, IC)
ax[2].set_title("Capacitor Current (iC)")
ax[2].set_ylabel("Current (A)")
ax[2].grid()

# Load Current
ax[3].plot(t*1e6, Io*np.ones_like(t))
ax[3].set_title("Load Current (Io)")
ax[3].set_xlabel("Time (µs)")
ax[3].set_ylabel("Current (A)")
ax[3].grid()

plt.tight_layout(h_pad=3)

st.pyplot(fig)

# ================= RESULTS =================
st.subheader("📊 Output")

c1, c2, c3 = st.columns(3)
c1.metric("Output Voltage", f"{Vo:.2f} V")
c2.metric("Load Current", f"{Io:.2f} A")
c3.metric("Inductor Ripple", f"{delta_IL:.4f} A")
