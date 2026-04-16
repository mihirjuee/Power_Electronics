import streamlit as st
import numpy as np
import plotly.graph_objects as go
import schemdraw
import schemdraw.elements as elm

# --- PAGE CONFIG ---
st.set_page_config(page_title="Learn EE - Centre Tapped Lab", layout="wide")

st.title("⚡ Centre-Tapped Full Wave Rectifier Lab")

# =========================
# 🔧 SIDEBAR PARAMETERS
# =========================
with st.sidebar:
    st.header("Transformer & Diode")
    Vm = st.slider("Secondary Peak Voltage (Vm per half)", 5, 100, 30)
    f = st.slider("Frequency (Hz)", 10, 100, 50)
    Vd = st.slider("Diode Forward Drop (Vd)", 0.0, 1.2, 0.7)
    
    st.divider()
    st.header("Filter & Load")
    R = st.slider("Load Resistance (R) [Ω]", 10, 2000, 500)
    C_micro = st.slider("Capacitance (C) [µF]", 0, 2000, 470)
    C = C_micro * 1e-6

# =========================
# ⏱ PHYSICS ENGINE
# =========================
t = np.linspace(0, 0.1, 3000)
dt = t[1] - t[0]

Va = Vm * np.sin(2 * np.pi * f * t)
Vb = -Va 

Vrect = np.maximum(np.maximum(Va, Vb) - Vd, 0)

Vout = np.zeros_like(t)
if C > 0:
    for i in range(1, len(t)):
        V_discharge = Vout[i-1] * np.exp(-dt / (R * C))
        Vout[i] = max(Vrect[i], V_discharge)
else:
    Vout = Vrect

Vdc = np.mean(Vout)
Idc = Vdc / R
piv = 2 * Vm

# =========================
# 🔌 CIRCUIT DIAGRAM
# =========================
st.subheader("🔌 Circuit Schematic")

def draw_centre_tap():
    # Use 'svg' or 'png'. 'png' is often more stable in Streamlit Cloud
    d = schemdraw.Drawing(show=False)
    
    # Transformer Primary
    L1 = d.add(elm.Inductor().label('Primary'))
    d.add(elm.Line().left().at(L1.start).length(0.5))
    d.add(elm.SourceSin().down().label('Vin'))
    d.add(elm.Line().right().length(0.5))
    
    # Core lines
    d.add(elm.Line().down().at((1.2, 0.2)).length(1.5).color('gray'))
    d.add(elm.Line().down().at((1.35, 0.2)).length(1.5).color('gray'))

    # Centre Tapped Secondary
    # Top half
    L2 = d.add(elm.Inductor().at((1.8, 0)).label('L2'))
    # Bottom half
    L3 = d.add(elm.Inductor().at((1.8, -1.5)).label('L3'))
    
    # Centre Tap connection
    tap = d.add(elm.Dot(at=(1.8, -0.75)))
    
    # Diodes - Using explicit coordinates to avoid the Point error
    d1 = d.add(elm.Diode().right().at((1.8, 0)).label('D1'))
    d2 = d.add(elm.Diode().right().at((1.8, -2.25)).label('D2'))
    
    # Cathode connection
    d.add(elm.Line().down().at(d1.end).to((d1.end[0], d2.end[1])))
    out_node = d.add(elm.Dot(at=(d1.end[0], -1.125)))
    
    # Load and Filter
    d.add(elm.Line().right().at(out_node.start).length(1.5))
    d.add(elm.Capacitor().down().label(f'{C_micro}µF'))
    d.add(elm.Line().right().length(1.5))
    d.add(elm.Resistor().down().label(f'{R}Ω'))
    
    # Return path to Centre Tap
    d.add(elm.Line().left().at(tap.start).to((d1.end[0] + 3, -0.75)))
    d.add(elm.Line().down().to((d1.end[0] + 3, -3.125)))
    d.add(elm.Line().left().to((1.8, -3.125)))

    return d.get_imagedata('png')

# Display with error handling
try:
    st.image(draw_centre_tap(), width=700)
except Exception as e:
    st.error(f"Schematic rendering error: {e}")

st.divider()

# =========================
# 📊 WAVEFORMS & METRICS
# =========================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Oscilloscope View")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=Va, name="Phase A", line=dict(color='blue', dash='dash', width=1)))
    fig.add_trace(go.Scatter(x=t, y=Vb, name="Phase B", line=dict(color='green', dash='dash', width=1)))
    fig.add_trace(go.Scatter(x=t, y=Vout, name="Vout", line=dict(color='red', width=3)))
    
    fig.update_layout(height=400, xaxis_title="Time (s)", yaxis_title="Voltage (V)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Performance Analysis")
    st.metric("Avg DC Voltage", f"{Vdc:.2f} V")
    st.metric("DC Current", f"{Idc*1000:.1f} mA")
    st.error(f"PIV Rating (Min): {piv} V")
    
    eff = (Vdc / Vm) * 100 if Vm > 0 else 0
    st.write(f"**Rectification Efficiency:** {eff:.1f}%")

st.info(f"Ripple frequency is {2*f} Hz. PIV is calculated as 2 * Vm = {piv}V.")
