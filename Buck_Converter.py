import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Buck Converter Pro", layout="wide")
st.title("⚡ Buck Converter (Industry-Level Simulator)")

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
t = np.linspace(0, 6*T, 4000)
dt = t[1] - t[0]

# ================= ARRAYS =================
IL = np.zeros_like(t)
Vo = np.zeros_like(t)
VL = np.zeros_like(t)

Vo[0] = D * Vin

# ================= SWITCHING SIM =================
for i in range(1, len(t)):

    if (t[i] % T) < (D * T):
        VL[i] = Vin - Vo[i-1]   # ON
    else:
        VL[i] = -Vo[i-1]        # OFF

    # Inductor current
    IL[i] = IL[i-1] + (VL[i] / L) * dt

    # Prevent negative current (DCM)
    if IL[i] < 0:
        IL[i] = 0

    # Capacitor current
    IC = IL[i] - Vo[i-1]/R

    # Voltage update
    Vo[i] = Vo[i-1] + (IC / C) * dt

# Derived
Io = Vo / R
IC_wave = IL - Io

# ================= STEADY STATE =================
steady = int(0.5 * len(t))

Vo_ss = Vo[steady:]
IL_ss = IL[steady:]
Io_ss = Io[steady:]

Vripple = np.max(Vo_ss) - np.min(Vo_ss)
Iripple = np.max(IL_ss) - np.min(IL_ss)

Vo_avg = np.mean(Vo_ss)
Io_avg = np.mean(Io_ss)

IL_rms = np.sqrt(np.mean(IL_ss**2))

# ================= MODE DETECTION =================
mode = "DCM" if np.min(IL_ss) <= 0 else "CCM"

# ================= EFFICIENCY (IDEAL) =================
Pin = Vin * np.mean(IL_ss)
Pout = Vo_avg * Io_avg
eff = (Pout / Pin) * 100 if Pin != 0 else 0

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

        return d.draw().fig

st.pyplot(draw_circuit())

# ================= WAVEFORMS =================
st.subheader("📈 Waveforms")

fig, ax = plt.subplots(5, 1, figsize=(10, 12), sharex=True)

ax[0].plot(t*1e6, Vo)
ax[0].set_title("Output Voltage")
ax[0].grid()

ax[1].plot(t*1e6, IL)
ax[1].set_title("Inductor Current")
ax[1].grid()

ax[2].plot(t*1e6, VL)
ax[2].set_title("Inductor Voltage")
ax[2].grid()

ax[3].plot(t*1e6, IC_wave)
ax[3].set_title("Capacitor Current")
ax[3].grid()

ax[4].plot(t*1e6, Io)
ax[4].set_title("Load Current")
ax[4].set_xlabel("Time (µs)")
ax[4].grid()

plt.tight_layout(h_pad=3)
st.pyplot(fig)

# ================= RIPPLE ZOOM =================
st.subheader("🔍 Output Ripple (Zoomed)")

fig2, ax2 = plt.subplots(figsize=(8,3))
ax2.plot(t[steady:]*1e6, Vo_ss)
ax2.set_title("Zoomed Output Voltage Ripple")
ax2.grid()

st.pyplot(fig2)

# ================= METRICS =================
st.subheader("📊 Performance Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Vo Avg", f"{Vo_avg:.2f} V")
c2.metric("Ripple (ΔVo)", f"{Vripple:.4f} V")
c3.metric("Inductor Ripple", f"{Iripple:.4f} A")
c4.metric("Efficiency", f"{eff:.2f} %")

c5, c6, c7 = st.columns(3)

c5.metric("Io Avg", f"{Io_avg:.2f} A")
c6.metric("IL RMS", f"{IL_rms:.2f} A")
c7.metric("Mode", mode)

# ================= INFO =================
st.success("Simulation includes switching dynamics, ripple analysis, and mode detection (CCM/DCM).")
