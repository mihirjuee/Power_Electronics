import streamlit as st
import numpy as np
import plotly.graph_objects as go
import schemdraw
import schemdraw.elements as elm

# --- PAGE CONFIG ---
st.set_page_config(page_title="Full Wave Rectifier Lab", layout="wide")

st.title("⚡ Full Wave Rectifier with Capacitor Filter")

# =========================
# 🔧 SIDEBAR
# =========================
with st.sidebar:
    st.header("Input Parameters")

    Vm = st.slider("Peak Voltage (Vm)", 10, 325, 100)
    f = st.slider("Frequency (Hz)", 10, 100, 50)
    R = st.slider("Load Resistance (Ω)", 10, 1000, 100)
    Vd = st.slider("Diode Drop (V)", 0.0, 1.5, 0.7)

    st.markdown("---")
    C_micro = st.slider("Capacitance (µF)", 1, 5000, 1000)
    C = C_micro * 1e-6

# =========================
# ⏱ TIME
# =========================
t = np.linspace(0, 0.1, 2000)
dt = t[1] - t[0]

# =========================
# ⚡ SIGNALS
# =========================
Vin = Vm * np.sin(2 * np.pi * f * t)

Vrect = np.abs(Vin) - 2 * Vd
Vrect[Vrect < 0] = 0

# =========================
# 🔋 CAP FILTER
# =========================
Vcap = np.zeros_like(t)

for i in range(1, len(t)):
    if Vrect[i] > Vcap[i-1]:
        Vcap[i] = Vrect[i]
    else:
        Vcap[i] = Vcap[i-1] * np.exp(-dt / (R * C))

# =========================
# 📊 CALCULATIONS
# =========================
Vdc = np.mean(Vcap)
Vripple = np.max(Vcap) - np.min(Vcap)
ripple_factor = Vripple / Vdc if Vdc != 0 else 0
Idc = Vdc / R if R != 0 else 0

# =========================
# 📊 LAYOUT
# =========================
col1, col2 = st.columns(2)

# --- WAVEFORM ---
with col1:
    st.subheader("📊 Waveforms")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=Vin, name="Input AC"))
    fig.add_trace(go.Scatter(x=t, y=Vrect, name="Rectified"))
    fig.add_trace(go.Scatter(x=t, y=Vcap, name="Filtered DC"))

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- METRICS ---
with col2:
    st.subheader("📈 Output")

    st.metric("DC Voltage", f"{Vdc:.2f} V")
    st.metric("Ripple Voltage", f"{Vripple:.2f} V")
    st.metric("Ripple Factor", f"{ripple_factor:.4f}")
    st.metric("Load Current", f"{Idc:.2f} A")

# =========================
# 🔌 CIRCUIT DIAGRAM (FINAL FIX)
# =========================
st.divider()
st.subheader("🔌 Circuit Diagram")

d = schemdraw.Drawing()

# AC Source
d += elm.SourceSin().label("AC")

# Bridge Rectifier
d += elm.Line().right()
d += elm.Diode().right().label("D1")
d += elm.Line().down()
d += elm.Diode().down().label("D2")
d += elm.Line().left()
d += elm.Diode().left().label("D3")
d += elm.Line().up()
d += elm.Diode().up().label("D4")

# Output
d += elm.Line().right().length(2)
d += elm.Capacitor().down().label("C")
d += elm.Resistor().down().label("R")
d += elm.Ground()

# ✅ SAFE RENDER (NO ERROR)
img = d.get_imagedata('svg')
st.image(img)

# =========================
# 📘 THEORY
# =========================
st.divider()
st.info(f"""
⚡ Full Wave Rectifier + Capacitor Filter

• Converts AC to DC  
• Capacitor reduces ripple  
• Ripple frequency = {2*f} Hz  

📉 Increase C → smoother output  
📉 Increase load → more ripple  

Formula:
Vr ≈ I / (f × C)
""")
