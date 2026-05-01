import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
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

# ================= CALCULATION =================
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

    # DCM condition
    if IL[i] < 0:
        IL[i] = 0

    IC = IL[i] - Vo[i-1] / R
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

# ================= CIRCUIT =================
st.subheader("🔌 Circuit Diagram")

with schemdraw.Drawing() as d:
    d += elm.SourceV().label(f'{Vin} V')
    d += elm.Line().right(1)
    d += elm.Line().up(0.01)
    d += elm.NFet().label("MOSFET")
    d += elm.Line().right(1)

    d.push()
    d += elm.Inductor().label('L')
    d += elm.Line().right(1)
    d += elm.Dot()

    d.push()
    d += elm.Capacitor().down().label('C')
    d.pop()

    d += elm.Line().right(1)
    d += elm.Resistor().down().label('R')
    d.pop()

    d += elm.Diode().down().label('D')
    

    fig_circuit = d.draw().fig

st.pyplot(fig_circuit)
st.metric("Operating Mode", mode)

# ================= WAVEFORMS =================
st.subheader("📈 Steady-State Waveforms")

fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Output Voltage
axes[0].plot(t[steady:] * 1e6, Vo_ss, color='red', linewidth=2, label="Vo")
axes[0].axhline(Vo_avg, linestyle='--', linewidth=1.5,
                label=f"Avg = {Vo_avg:.2f} V")

# Ripple band visualization
axes[0].fill_between(
    t[steady:] * 1e6,
    Vo_avg - Vripple/2,
    Vo_avg + Vripple/2,
    alpha=0.2,
    label="Ripple Band"
)

axes[0].set_ylabel("Vo (V)")
axes[0].set_title("Output Voltage")
axes[0].legend()
axes[0].grid(True)

# Inductor Current
axes[1].plot(t[steady:] * 1e6, IL_ss, color='blue')
axes[1].set_ylabel("iL (A)")
axes[1].set_title("Inductor Current")
axes[1].grid(True)

# Inductor Voltage
axes[2].plot(t[steady:] * 1e6, VL_ss, color='green')
axes[2].set_ylabel("VL (V)")
axes[2].set_xlabel("Time (µs)")
axes[2].set_title("Inductor Voltage")
axes[2].grid(True)

plt.tight_layout(h_pad=3)
st.pyplot(fig)

# ================= RIPPLE ZOOM =================
st.subheader("🔍 Output Voltage Ripple (Zoomed)")

fig2, ax2 = plt.subplots(figsize=(8, 3))
ax2.plot(t[steady:] * 1e6, Vo_ss)
ax2.set_ylim(Vo_avg - 2*Vripple, Vo_avg + 2*Vripple)
ax2.set_xlabel("Time (µs)")
ax2.set_ylabel("Voltage (V)")
ax2.grid(True)

st.pyplot(fig2)

# ================= METRICS =================
st.subheader("📊 Key Performance Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Vo Avg", f"{Vo_avg:.2f} V")
c2.metric("Ripple (ΔVo)", f"{Vripple:.4f} V")
c3.metric("Ripple %", f"{ripple_pct:.2f} %")
c4.metric("Efficiency", f"{eff:.2f} %")

c5, c6 = st.columns(2)
c5.metric("Inductor Peak Current", f"{IL_peak:.2f} A")
c6.metric("Mode", mode)

# ================= INFO =================
st.info("Ripple % = (ΔVo / Vo_avg) × 100. Ideal model (no losses).")
