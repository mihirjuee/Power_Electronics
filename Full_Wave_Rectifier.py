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
    Vd = st.slider("Diode Forward Drop (Vd)", 0.0, 1.5, 0.7)
    
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

# Phase A and Phase B are 180 degrees apart
Va = Vm * np.sin(2 * np.pi * f * t)
Vb = -Va 

# Full wave rectification (Single diode drop)
Vrect = np.maximum(np.maximum(Va, Vb) - Vd, 0)

# Filter Logic (Capacitor Discharge calculation)
Vout = np.zeros_like(t)
if C > 0:
    for i in range(1, len(t)):
        V_discharge = Vout[i-1] * np.exp(-dt / (R * C))
        Vout[i] = max(Vrect[i], V_discharge)
else:
    Vout = Vrect

# Quantitative Analysis
Vdc = np.mean(Vout)
Idc = Vdc / R
piv = 2 * Vm

# =========================
# 🔌 CIRCUIT DIAGRAM
# =========================
st.subheader("🔌 Circuit Schematic")

def draw_centre_tap():
    d = schemdraw.Drawing(show=False)
    
    # Transformer Primary
    S = d.add(elm.SourceSin().label('Primary'))
    
    # Centre Tapped Secondary logic
    d.add(elm.Line().right().at(S.end).length(1))
    d.add(elm.Inductor2().down().label('L1'))
    tap = d.add(elm.Dot())
    d.add(elm.Inductor2().down().label('L2'))
    d.add(elm.Line().left().length(1))
    
    # Diodes
    d1 = d.add(elm.Diode().right().at(S.end + (1,0)).label('D1'))
    d2 = d.add(elm.Diode().right().at(S.end + (1,-4.5)).label('D2'))
    
    # Connection to Load
    d.add(elm.Line().down().at(d1.end).to(d2.end))
    mid = d.add(elm.Dot(at=d1.end + (0,-2.25)))
    
    d.add(elm.Line().right().at(mid.start).length(1))
    d.add(elm.Capacitor().down().label(f'{C_micro}µF'))
    d.add(elm.Line().right().length(1.5))
    d.add(elm.Resistor().down().label(f'{R}Ω'))
    
    # Return to Centre Tap ground path
    d.add(elm.Line().left().at(tap.start).length(4.5))
    
    return d.get_imagedata('png')

# Display the diagram
st.image(draw_centre_tap(), width=700)

st.divider()

# =========================
# 📊 WAVEFORMS & METRICS
# =========================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Oscilloscope View")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=Va, name="Phase A (Top)", line=dict(color='blue', dash='dash', width=1)))
    fig.add_trace(go.Scatter(x=t, y=Vb, name="Phase B (Bottom)", line=dict(color='green', dash='dash', width=1)))
    fig.add_trace(go.Scatter(x=t, y=Vout, name="Vout (Load)", line=dict(color='red', width=3)))
    
    fig.update_layout(
        height=400, 
        xaxis_title="Time (s)", 
        yaxis_title="Voltage (V)", 
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Performance Analysis")
    st.metric("Avg DC Voltage", f"{Vdc:.2f} V")
    st.metric("DC Current", f"{Idc*1000:.1f} mA")
    st.error(f"PIV Rating (Min): {piv} V")
    
    # Efficiency calculation
    eff = (Vdc / Vm) * 100 if Vm > 0 else 0
    st.write(f"**Rectification Efficiency:** {eff:.1f}%")

# =========================
# 📘 THEORY SUMMARY
# =========================
st.info(f"""
**Key Lab Observations:**
1. **PIV Calculation:** For a centre-tapped rectifier, each diode must withstand $2V_m$. In this case, that is **{piv}V**.
2. **Frequency:** The output ripple frequency is $2f = {2*f} Hz$.
3. **Diode Drop:** Note that only one diode conducts per half-cycle, resulting in a single $V_d$ ({Vd}V) loss from the peak.
""")
