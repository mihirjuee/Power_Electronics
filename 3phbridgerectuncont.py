import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="3-Phase Rectifier", page_icon="logo.png", layout="wide")

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

# ================= CIRCUIT DIAGRAM (FULL 6-DIODE BRIDGE) =================
# ================= CIRCUIT DIAGRAM (3-PHASE RECTIFIER WITH SOURCES) =================
st.subheader("🔌 Full 3-Phase Rectifier Bridge")

with schemdraw.Drawing() as d:
    # --- AC Sources ---
    d += elm.Dot()
    d.push() 
    d += (S1 := elm.SourceSin().up().label("Vb"))
    d += elm.Line().left()
    d += (S1 := elm.SourceSin().up().label("Va"))
    d.pop()
    d += (S1 := elm.SourceSin().up().label("Vc"))
    
    
    # --- Bridge Legs ---
    # Leg 1: A
    d += (D1 := elm.Diode().at(S1.end).up().label("D1"))
    d += (D4 := elm.Diode().at(S1.end).down().label("D4"))
    
    # Leg 2: B
    d += (D3 := elm.Diode().at(S2.end).up().label("D3"))
    d += (D6 := elm.Diode().at(S2.end).down().label("D6"))
    
    # Leg 3: C
    d += (D5 := elm.Diode().at(S3.end).up().label("D5"))
    d += (D2 := elm.Diode().at(S3.end).down().label("D2"))
    
    # --- Connecting the DC Load ---
    d += elm.Line().at(D1.end).to(D3.end).to(D5.end)
    d += (R := elm.Resistor().at(D5.end).right().label("Load"))
    d += elm.Line().at(D4.end).to(D6.end).to(D2.end).right().to(R.start)

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
