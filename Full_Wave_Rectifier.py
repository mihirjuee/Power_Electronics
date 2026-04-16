import streamlit as st
import numpy as np
import plotly.graph_objects as go
import schemdraw
import schemdraw.elements as elm

# --- PAGE CONFIG ---
st.set_page_config(page_title="Full Wave Rectifier Lab", layout="wide")

st.title("⚡ Full Wave Rectifier with Capacitor Filter")
st.write("Interactive AC to DC conversion with ripple reduction")

# =========================
# 🔧 SIDEBAR INPUTS
# =========================
with st.sidebar:
    st.header("Input Parameters")

    Vm = st.slider("Peak Voltage (Vm)", 10, 325, 100)
    f = st.slider("Frequency (Hz)", 10, 100, 50)
    R = st.slider("Load Resistance (Ω)", 10, 1000, 100)
    Vd = st.slider("Diode Drop (V)", 0.0, 1.5, 0.7)

    st.markdown("---")
    st.header("Filter")

    C_micro = st.slider("Capacitance (µF)", 1, 5000, 1000)
    C = C_micro * 1e-6

# =========================
# ⏱ TIME AXIS
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
# 🔋 CAPACITOR FILTER
# =========================
Vcap = np.zeros_like(t)

for i in range(1, len(t)):
    if Vrect[i] > Vcap[i - 1]:
        Vcap[i] = Vrect[i]  # charging
    else:
        Vcap[i] = Vcap[i - 1] * np.exp(-dt / (R * C))  # discharging

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

# --- WAVEFORMS ---
with col1:
    st.subheader("📊 Waveforms")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=Vin, name="Input AC"))
    fig.add_trace(go.Scatter(x=t, y=Vrect, name="Rectified Output"))
    fig.add_trace(go.Scatter(x=t, y=Vcap, name="Filtered Output"))

    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Voltage (V)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# --- METRICS ---
with col2:
    st.subheader("📈 Output Parameters")

    st.metric("DC Voltage", f"{Vdc:.2f} V")
    st.metric("Ripple Voltage", f"{Vripple:.2f} V")
    st.metric("Ripple Factor", f"{ripple_factor:.4f}")
    st.metric("Load Current", f"{Idc:.2f} A")

# =========================
# 🔌 CIRCUIT DIAGRAM (FIXED)
# =========================
st.divider()
st.subheader("🔌 Circuit Diagram")

d = schemdraw.Drawing()

# AC source
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

# Output side
d += elm.Line().right().length(2)

# Capacitor
d += elm.Capacitor().down().label("C")

# Load resistor
d += elm.Resistor().down().label("R")

# Ground
d += elm.Ground()

# ✅ FIXED RENDERING
fig_diag = d.draw(show=False)
st.pyplot(fig_diag)

# =========================
# 📘 THEORY
# =========================
st.divider()
st.info(f"""
⚡ **Working Principle**

• Full-wave rectifier converts both halves of AC into DC  
• Capacitor smooths output by storing charge  
• Ripple frequency = {2*f} Hz  

📉 **Observations**
- Increase capacitance → ripple decreases  
- Increase load → ripple increases  

📐 **Formula**
Vr ≈ I / (f × C)
""")
