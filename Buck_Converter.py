import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Buck Converter Analysis", layout="wide")
st.title("⚡ Buck Converter: Circuit & Waveforms")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Parameters")
Vin = st.sidebar.number_input("Input Voltage (V)", 12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 1.0, 0.5)
fs = st.sidebar.number_input("Switching Frequency (Hz)", 20000.0)
R = st.sidebar.number_input("Load Resistance (Ω)", 10.0)
L = st.sidebar.number_input("Inductance (H)", 1e-3, format="%.5f")
C = st.sidebar.number_input("Capacitance (F)", 100e-6, format="%.6f")

# ================= CIRCUIT DIAGRAM =================
def draw_circuit():
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
    return d

st.subheader("Circuit Topology")
st.write(draw_circuit()) # This renders the diagram directly in Streamlit

# 

# ================= CALCULATIONS & PLOTTING =================
T = 1 / fs
Vo = D * Vin
IL_avg = Vo / R
delta_IL = (Vin - Vo) * (D * T) / L
t = np.linspace(0, T, 1000)

# Waveforms
iL = np.where(t < D * T, IL_avg - delta_IL/2 + (Vin - Vo)*t/L, IL_avg + delta_IL/2 - (Vo*(t - D*T)/L))
ic = iL - IL_avg
vo = Vo + (delta_IL * T) / (8 * C) * np.sin(2 * np.pi * fs * t) # Simplified ripple

st.subheader("Steady-State Waveforms")
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
ax1.plot(t*1e6, iL, 'b'); ax1.set_ylabel("iL (A)"); ax1.grid(True)
ax2.plot(t*1e6, ic, 'g'); ax2.set_ylabel("iC (A)"); ax2.grid(True)
ax3.plot(t*1e6, vo, 'r'); ax3.set_ylabel("Vo (V)"); ax3.set_xlabel("Time (µs)"); ax3.grid(True)
st.pyplot(fig)
