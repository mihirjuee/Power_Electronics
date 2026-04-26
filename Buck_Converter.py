import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE SETUP =================
st.set_page_config(page_title="Buck Converter Pro", layout="wide")
st.title("⚡ Buck Converter Analysis Tool")

# ================= SIDEBAR =================
st.sidebar.header("🔧 System Parameters")

Vin = st.sidebar.number_input("Input Voltage (V)", value=12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 1.0, 0.5)
fs = st.sidebar.number_input("Switching Frequency (Hz)", value=20000.0)

R = st.sidebar.number_input("Load Resistance (Ω)", value=10.0)
L = st.sidebar.number_input("Inductance (H)", value=1e-3, format="%.5f")
C = st.sidebar.number_input("Capacitance (F)", value=100e-6, format="%.6f")

# ================= SIMULATION =================
T = 1 / fs
t = np.linspace(0, 10*T, 5000)
dt = t[1] - t[0]

IL = np.zeros_like(t)
Vo = np.zeros_like(t)
VL = np.zeros_like(t)

Vo[0] = D * Vin

for i in range(1, len(t)):

    switch = 1 if (t[i] % T) < (D * T) else 0
    VL[i] = (switch * Vin) - Vo[i-1]

    IL[i] = IL[i-1] + (VL[i] / L) * dt

    if IL[i] < 0:
        IL[i] = 0

    IC = IL[i] - (Vo[i-1] / R)
    Vo[i] = Vo[i-1] + (IC / C) * dt

# ================= STEADY STATE =================
steady = int(0.6 * len(t))

Vo_ss = Vo[steady:]
IL_ss = IL[steady:]
VL_ss = VL[steady:]

Vo_avg = np.mean(Vo_ss)
Vripple = np.max(Vo_ss) - np.min(Vo_ss)
ripple_pct = (Vripple / Vo_avg) * 100 if Vo_avg != 0 else 0
IL_peak = np.max(IL_ss)

Pin = Vin * np.mean(IL_ss)
Pout = Vo_avg**2 / R
eff = (Pout / Pin) * 100 if Pin != 0 else 0

mode = "DCM" if np.min(IL_ss) <= 1e-3 else "CCM"

# ================= CIRCUIT (TOP) =================
st.subheader("🔌 Circuit Diagram")

with schemdraw.Drawing() as d:
    d += elm.SourceV().label(f'{Vin} V')
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
    st.pyplot(fig.fig)

st.metric("Operating Mode", mode)

# ================= WAVEFORMS (MIDDLE) =================
st.subheader("📈 Steady-State Waveforms")

fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

axes[0].plot(t[steady:] * 1e6, Vo_ss, 'r')
axes[0].set_ylabel("Vo (V)")
axes[0].set_title("Output Voltage")
axes[0].grid(True)

axes[1].plot(t[steady:] * 1e6, IL_ss, 'b')
axes[1].set_ylabel("iL (A)")
axes[1].set_title("Inductor Current")
axes[1].grid(True)

axes[2].plot(t[steady:] * 1e6, VL_ss, 'g')
axes[2].set_ylabel("VL (V)")
axes[2].set_xlabel("Time (µs)")
axes[2].set_title("Inductor Voltage")
axes[2].grid(True)

plt.tight_layout(h_pad=3)
st.pyplot(fig)

# ================= METRICS (BOTTOM) =================
st.subheader("📊 Key Performance Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Vo Avg", f"{Vo_avg:.2f} V")
c2.metric("Ripple (ΔVo)", f"{Vripple:.4f} V")
c3.metric("Ripple %", f"{ripple_pct:.2f} %")
c4.metric("Efficiency", f"{eff:.1f} %")

c5, c6 = st.columns(2)
c5.metric("Inductor Peak Current", f"{IL_peak:.2f} A")
c6.metric("Mode", mode)

# ================= INFO =================
st.info("Layout updated: Circuit → Waveforms → Metrics for better readability.")
