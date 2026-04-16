import streamlit as st
import numpy as np
import plotly.graph_objects as go
import schemdraw
import schemdraw.elements as elm
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Learn EE - Full Wave Rectifier", layout="wide")

st.title("⚡ Full Wave Bridge Rectifier with Capacitor Filter")

# =========================
# 🔧 SIDEBAR
# =========================
with st.sidebar:
    st.header("Simulation Settings")
    Vm = st.slider("Peak Voltage (Vm)", 10.0, 325.0, 100.0)
    f = st.slider("Frequency (Hz)", 10, 100, 50)
    R = st.slider("Load Resistance (Ω)", 10, 2000, 500)
    Vd = st.slider("Diode Forward Drop (V)", 0.0, 1.2, 0.7)
    
    st.markdown("---")
    C_micro = st.slider("Capacitance (µF)", 0, 5000, 1000)
    C = C_micro * 1e-6

# =========================
# ⏱ MATH ENGINE
# =========================
t = np.linspace(0, 0.1, 3000)
dt = t[1] - t[0]
Vin = Vm * np.sin(2 * np.pi * f * t)

# Full Wave Rectification (2*Vd drop for bridge)
Vrect = np.abs(Vin) - (2 * Vd)
Vrect = np.maximum(Vrect, 0)

# Filter Logic (Capacitor Discharge)
Vcap = np.zeros_like(t)
if C > 0:
    for i in range(1, len(t)):
        # Discharge phase
        V_discharge = Vcap[i-1] * np.exp(-dt / (R * C))
        # Charging phase: Cap voltage follows Rectified voltage if Rectified is higher
        Vcap[i] = max(Vrect[i], V_discharge)
else:
    Vcap = Vrect

# Metrics
Vdc = np.mean(Vcap)
Vripple = np.max(Vcap[-500:]) - np.min(Vcap[-500:]) # Use steady state portion
ripple_factor = Vripple / Vdc if Vdc > 0.1 else 0

# =========================
# 📊 UI LAYOUT
# =========================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Signal Analysis")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=Vin, name="Input AC", line=dict(color='gray', dash='dash')))
    fig.add_trace(go.Scatter(x=t, y=Vrect, name="Rectified (Unfiltered)", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=t, y=Vcap, name="Filtered DC Output", line=dict(color='red', width=3)))
    
    fig.update_layout(height=450, xaxis_title="Time (s)", yaxis_title="Voltage (V)", legend_orientation="h")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Performance Metrics")
    st.metric("Mean DC Voltage", f"{Vdc:.2f} V")
    st.metric("Peak-to-Peak Ripple", f"{Vripple:.2f} V")
    st.metric("Ripple Factor", f"{ripple_factor:.4f}")
    
    # Visual Efficiency Meter
    efficiency = (Vdc / Vm) * 100
    st.progress(min(int(efficiency), 100))
    st.caption(f"Conversion Efficiency: {efficiency:.1f}%")

# =========================
# 🔌 CIRCUIT SCHEMATIC
# =========================
st.divider()
st.subheader("🔌 Circuit Schematic")

# Using a more reliable render method for Streamlit
def draw_bridge():
    d = schemdraw.Drawing(show=False)
    # Source
    S = d.add(elm.SourceSin().label('Vin'))
    d.add(elm.Line().right().at(S.start))
    d.add(elm.Line().right().at(S.end))
    
    # Bridge
    B = d.add(elm.Rectifier().at((3, 0)).label('Bridge'))
    
    # Filter and Load
    d.add(elm.Line().right().at(B.E))
    d.add(elm.Capacitor().down().label(f'{C_micro}µF'))
    d.add(elm.Line().right().length(1.5))
    d.add(elm.Resistor().down().label(f'{R}Ω'))
    d.add(elm.Line().left().length(3.5))
    
    # Convert to bytes for st.image
    img_bytes = d.get_imagedata('png')
    return img_bytes

st.image(draw_bridge(), width=600)

# =========================
# 📘 QUICK THEORY
# =========================
st.info(f"""
**Key Insights for this Simulation:**
* **Diode Drop:** In a Bridge Rectifier, the current always passes through **two** diodes, so the total drop is $2 \times V_d$ (approx {2*Vd}V).
* **Ripple Frequency:** Notice the rectified peaks occur at **{2*f} Hz**. The capacitor has less time to discharge compared to a half-wave rectifier, resulting in a lower ripple factor.
* **RC Time Constant:** The discharge is governed by $\\tau = R \\times C$. Currently, $\\tau$ = {R*C:.4f} seconds.
""")
