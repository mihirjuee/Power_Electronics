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

# ================= SIMULATION ENGINE =================
T = 1 / fs
t = np.linspace(0, 10*T, 5000)
dt = t[1] - t[0]

IL = np.zeros_like(t)
Vo = np.zeros_like(t)
VL = np.zeros_like(t)

for i in range(1, len(t)):
    # Switch state: 1 for ON, 0 for OFF
    switch = 1 if (t[i] % T) < (D * T) else 0
    
    # Differential Equations
    VL[i] = (switch * Vin) - Vo[i-1]
    IL[i] = IL[i-1] + (VL[i] / L) * dt
    
    # DCM Protection
    if IL[i] < 0: IL[i] = 0
    
    # Output voltage update
    IC = IL[i] - (Vo[i-1] / R)
    Vo[i] = Vo[i-1] + (IC / C) * dt

# ================= ANALYSIS =================
steady = int(0.6 * len(t))
Vo_ss, IL_ss = Vo[steady:], IL[steady:]
Vripple = np.max(Vo_ss) - np.min(Vo_ss)
mode = "DCM" if np.min(IL_ss) <= 1e-3 else "CCM"

# ================= VISUALIZATION =================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Circuit Topology")
    d = schemdraw.Drawing()
    d += elm.SourceV().label(f'{Vin}V')
    d += elm.Line().right()
    d += elm.NFet().label("MOSFET")
    d += elm.Line().right()
    d.push()
    d += elm.Inductor().label('L')
    d += elm.Line().right()
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
    
    # Fix for schemdraw/Streamlit integration
    fig_circuit = d.draw()
    st.pyplot(fig_circuit)
    
    st.metric("Operating Mode", mode)

with col2:
    st.subheader("Steady-State Waveforms")
    fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
    axes[0].plot(t[steady:]*1e6, Vo_ss, 'r'); axes[0].set_ylabel("Vo (V)"); axes[0].grid(True)
    axes[1].plot(t[steady:]*1e6, IL_ss, 'b'); axes[1].set_ylabel("iL (A)"); axes[1].grid(True)
    axes[2].plot(t[steady:]*1e6, VL[steady:], 'g'); axes[2].set_ylabel("VL (V)"); axes[2].set_xlabel("Time (µs)"); axes[2].grid(True)
    st.pyplot(fig)

st.subheader("📊 Key Performance Metrics")
st.table({
    "Parameter": ["Avg Output Voltage", "Voltage Ripple", "Inductor Peak Current", "Efficiency"],
    "Value": [f"{np.mean(Vo_ss):.2f} V", f"{Vripple:.4f} V", f"{np.max(IL_ss):.2f} A", f"~{(np.mean(Vo_ss**2)/R)/(Vin*np.mean(IL_ss))*100:.1f} %"]
})
