import streamlit as st
import numpy as np
import plotly.graph_objects as go
import schemdraw
import schemdraw.elements as elm

# --- PAGE CONFIG ---
st.set_page_config(page_title="Full Wave Rectifier Lab", layout="wide")

st.title("⚡ Full Wave Rectifier with Capacitor Filter")
st.write("Interactive simulation of AC to DC conversion with ripple reduction")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🔧 Input Parameters")

    Vm = st.slider("Peak Voltage (Vm)", 10, 325, 100)
    f = st.slider("Frequency (Hz)", 10, 100, 50)
    R = st.slider("Load Resistance (Ω)", 10, 1000, 100)
    Vd = st.slider("Diode Drop (V)", 0.0, 1.5, 0.7)

    st.markdown("---")
    st.header("🔋 Filter Capacitor")

    C_micro = st.slider("Capacitance (µF)", 1, 5000, 1000)
    C = C_micro * 1e-6

# --- TIME AXIS ---
t = np.linspace(0, 0.1, 2000)
dt = t[1] - t[0]

# --- INPUT AC SIGNAL ---
Vin = Vm * np.sin(2 * np.pi * f * t)

# --- RECTIFIED OUTPUT ---
Vrect = np.abs(Vin) - 2 * Vd
Vrect[Vrect < 0] = 0

# --- CAPACITOR FILTER ---
Vcap = np.zeros_like(t)

for i in range(1, len(t)):
    if Vrect[i] > Vcap[i-1]:
        Vcap[i] = Vrect[i]  # Charging
    else:
        Vcap[i] = Vcap[i-1] * np.exp(-dt / (R * C))  # Discharging

# --- CALCULATIONS ---
Vdc = np.mean(Vcap)
Vripple = np.max(Vcap) - np.min(Vcap)
ripple_factor = Vripple / Vdc if Vdc != 0 else 0
Idc = Vdc / R if R != 0 else 0

# --- LAYOUT ---
col1, col2 = st.columns(2)

# =========================
# 📊 WAVEFORMS
# =========================
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

# =========================
# 📈 OUTPUT METRICS
# =========================
with col2:
    st.subheader("📈 Output Parameters")

    st.metric("DC Voltage (Vdc)", f"{Vdc:.2f} V")
    st.metric("Ripple Voltage", f"{Vripple:.2f} V")
    st.metric("Ripple Factor", f"{ripple_factor:.4f}")
    st.metric("Load Current", f"{Idc:.2f} A")

# =========================
# 🔌 CIRCUIT DIAGRAM
# =========================
st.divider()
st.subheader("🔌 Circuit Diagram: Full Wave Bridge Rectifier with Filter")

with schemdraw.Drawing() as d:

    # AC Source
    source = d.add(elm.SourceSin().label("AC Supply"))

    # Move right
    d += elm.Line().right()

    # Bridge - Top diode
    d += elm.Diode().right().label("D1")

    # Top right node
    d += elm.Line().down()

    # Right diode
    d += elm.Diode().down().label("D2")

    # Bottom node
    d += elm.Line().left()

    # Bottom diode
    d += elm.Diode().left().label("D3")

    # Left diode
    d += elm.Diode().up().label("D4")

    # Output line
    d += elm.Line().right().length(2)

    # Capacitor
    d += elm.Capacitor().down().label("C")

    # Load resistor
    d += elm.Resistor().down().label("R Load")

    # Ground
    d += elm.Ground()

    st.pyplot(d.draw())

# =========================
# 📘 THEORY
# =========================
st.divider()
st.info(f"""
⚡ **Working Principle:**

• Full-wave rectifier converts both halves of AC into DC  
• Capacitor charges at peaks and discharges slowly  
• This reduces ripple significantly  

📉 **Ripple Frequency:** {2*f} Hz  

📊 **Key Insight:**
- Increase capacitance → smoother output  
- Increase load current → more ripple  

📐 Approx Formula:
Vr ≈ I / (f × C)
""")
