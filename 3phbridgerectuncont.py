import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="3-Phase Rectifier", layout="wide")

st.title("⚡ 3-Phase Uncontrolled Rectifier (6-Pulse)")

st.latex(r"V_{dc} = 1.35 \times V_{LL}")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Input Parameters")
V_ll = st.sidebar.slider("Line Voltage V_LL (RMS)", 100, 500, 400)
f = st.sidebar.slider("Frequency (Hz)", 25, 60, 50)

# ================= CALCULATIONS =================
Vm = np.sqrt(2) * (V_ll / np.sqrt(3))
t = np.linspace(0, 2*np.pi, 1000)

Va = Vm * np.sin(t)
Vb = Vm * np.sin(t - 2*np.pi/3)
Vc = Vm * np.sin(t - 4*np.pi/3)

# DC calculation based on line-to-line envelopes
Vdc = np.maximum.reduce([Va-Vb, Va-Vc, Vb-Va, Vb-Vc, Vc-Va, Vc-Vb])
Vdc_avg = np.mean(Vdc)

# ================= METRICS =================
col1, col2 = st.columns(2)
col1.metric("Average DC Output Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Expected (1.35 × V_LL)", f"{1.35 * V_ll:.2f} V")

# ================= CIRCUIT DIAGRAM =================
st.subheader("🔌 Circuit Diagram")

with schemdraw.Drawing() as d:
    d += elm.SourceSin().label("R")
    d += elm.Line().right()
    d += (D1 := elm.Diode().up().label("D1"))
    d += elm.Line().right()
    d += elm.Dot()
    d += (Rload := elm.Resistor().down().label("Load"))
    d += elm.Dot()
    d += elm.Line().left()
    d += (D4 := elm.Diode().down().label("D4"))
    d += elm.Line().left()
    # Note: A full bridge requires 6 diodes; this snippet shows 
    # the concept of one leg for brevity in the drawing block.

# Display the diagram
st.image(d.get_imagedata('png'))

# ================= PLOTS =================
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax[0].plot(t, Va, label="Va")
ax[0].plot(t, Vb, label="Vb")
ax[0].plot(t, Vc, label="Vc")
ax[0].set_title("Three Phase Input Voltages")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(t, Vdc, color='orange')
ax[1].set_title("Rectified Output Voltage (6-Pulse)")
ax[1].grid(True)
ax[1].set_xlabel("Electrical Angle (rad)")

st.pyplot(fig)
