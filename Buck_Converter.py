import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Buck Converter Advanced", layout="wide")
st.title("⚡ Buck Converter (Switching Simulation)")

st.latex(r"V_o = D \cdot V_{in}")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Controls")

Vin = st.sidebar.number_input("Input Voltage (V)", value=12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 1.0, 0.5)
fs = st.sidebar.number_input("Switching Frequency (Hz)", value=20000.0)

R = st.sidebar.number_input("Load Resistance (Ω)", value=10.0)
L = st.sidebar.number_input("Inductance (H)", value=1e-3, format="%.5f")
C = st.sidebar.number_input("Capacitance (F)", value=100e-6, format="%.6f")

# ================= TIME =================
T = 1 / fs
t = np.linspace(0, 5*T, 3000)
dt = t[1] - t[0]

# ================= ARRAYS =================
IL = np.zeros_like(t)
Vo_wave = np.zeros_like(t)

# Initial condition
Vo_wave[0] = D * Vin

# ================= SWITCHING SIMULATION =================
for i in range(1, len(t)):

    # PWM logic
    if (t[i] % T) < (D * T):
        VL = Vin - Vo_wave[i-1]   # MOSFET ON
    else:
        VL = -Vo_wave[i-1]        # MOSFET OFF

    # Inductor current update
    IL[i] = IL[i-1] + (VL / L) * dt

    # Capacitor current
    IC = IL[i] - Vo_wave[i-1]/R

    # Capacitor voltage update
    Vo_wave[i] = Vo_wave[i-1] + (IC / C) * dt

# Derived quantities
Io_wave = Vo_wave / R
IC_wave = IL - Io_wave

# ================= RIPPLE CALCULATION =================
# Ignore initial transient (first cycle)
steady_start = int(0.5 * len(t))

Vo_steady = Vo_wave[steady_start:]
Vripple = np.max(Vo_steady) - np.min(Vo_steady)

Vo_avg = np.mean(Vo_steady)
Io_avg = np.mean(Io_wave[steady_start:])

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

# Output voltage
ax[0].plot(t*1e6, Vo_wave)
ax[0].set_title("Output Voltage (Vo)")
ax[0].set_ylabel("Voltage (V)")
ax[0].grid()

# Inductor current
ax[1].plot(t*1e6, IL)
ax[1].set_title("Inductor Current (iL)")
ax[1].set_ylabel("Current (A)")
ax[1].grid()

# Capacitor current
ax[2].plot(t*1e6, IC_wave)
ax[2].set_title("Capacitor Current (iC)")
ax[2].set_ylabel("Current (A)")
ax[2].grid()

# Load current
ax[3].plot(t*1e6, Io_wave)
ax[3].set_title("Load Current (Io)")
ax[3].set_xlabel("Time (µs)")
ax[3].set_ylabel("Current (A)")
ax[3].grid()

plt.tight_layout(h_pad=3)
st.pyplot(fig)

# ================= RESULTS =================
st.subheader("📊 Output")

c1, c2, c3 = st.columns(3)
c1.metric("Average Output Voltage", f"{Vo_avg:.2f} V")
c2.metric("Average Load Current", f"{Io_avg:.2f} A")
c3.metric("Output Voltage Ripple", f"{Vripple:.4f} V")

# ================= INFO =================
st.info("This simulation uses time-domain switching equations. Initial transient is ignored for ripple calculation.")
