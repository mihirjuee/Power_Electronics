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
st.subheader("🔌 Full 3-Phase Rectifier Bridge")

import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing() as d:

    # ================= AC SOURCES =================
    d += elm.Line().at((0, 0)).right(1)
    S1 = d.add(elm.SourceSin().right().label("Van"))
    d += elm.Dot()
    d += elm.Line().at((0, 2)).right(1)
    S2 = d.add(elm.SourceSin().right().label("Vbn"))
    d += elm.Line().right(1)
    
    d += elm.Line().at((0, 4)).right(1)
    S3 = d.add(elm.SourceSin().right().label("Vcn"))
    d += elm.Line().right(2)
    

    # ================= TOP DIODES =================
    d += elm.Line().at(S1.end).up(4.5)
    D1 = d.add(elm.Diode().up(2).label("D1"))
    d += elm.Line().up(0.5)
    d.push()
    d += elm.Line().at(S2.end).right(2)
    d.push()
    d += elm.Dot()
    d += elm.Line().up(2)
    D3 = d.add(elm.Diode().up().label("D3"))
    #d += elm.Line().up(0.25)
    d += elm.Line().at(S3.end).right(3.5)
    d.push()
    d += elm.Dot()
    D5 = d.add(elm.Diode().up().label("D5"))
    d.pop()
    d += elm.Line().down(4)
    D2 = d.add(elm.Diode().down().reverse().label("D2"))
    #d += elm.Line().down(0.5)
    # ================= BOTTOM DIODES =================
    D4 = d.add(elm.Diode().at(S1.end).down().reverse().label("D4"))
    d.pop()
    d += elm.Line().down(2)
    D6 = d.add(elm.Diode().down().reverse().label("D6"))
    d += elm.Line().at(S3.end).right(1)
    

    # ================= DC BUS (TOP) =================
    d.pop()
    d += elm.Line().right(2)
    d += elm.Line().to(D5.end)

    # ================= LOAD =================
    d += elm.Line().right(2)
    d += elm.Line().down(3.5)
    R = d.add(elm.Resistor().down().label("Load"))
    d += elm.Line().down(3.5)
    d += elm.Line().left(2)
    # ================= DC BUS (BOTTOM) =================
    d += elm.Line().at(D4.end).to(D6.end)
    d += elm.Line().to(D2.end)
    #d += elm.Line().right().to(R.start)
    d += elm.Line().at((0, 0)).up(4)
    d += elm.Dot().at((0, 2)).label("n", loc="left")
# ===== DISPLAY FIX =====
import io
from PIL import Image
import matplotlib.pyplot as plt

buf = io.BytesIO()
d.save(buf)
buf.seek(0)

img = Image.open(buf)

fig, ax = plt.subplots()
ax.imshow(img)
ax.axis('off')

st.pyplot(fig)

# ================= PLOTS =================
# ================= CALCULATIONS & PLOTS =================
# Convert radians to degrees for plotting
t_deg = np.rad2deg(t)

# Define Line-to-Line voltages
Vab = Va - Vb
Vbc = Vb - Vc
Vca = Vc - Va

fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

# Top Plot: Phase Voltages + Line Voltages (faintly)
ax[0].plot(t_deg, Va, label="Va", alpha=0.5)
ax[0].plot(t_deg, Vb, label="Vb", alpha=0.5)
ax[0].plot(t_deg, Vc, label="Vc", alpha=0.5)
ax[0].plot(t_deg, Vab, label="Vab", linestyle='--', color='k', alpha=0.3)
ax[0].set_title("Input Phase Voltages & Line Voltage Envelopes")
ax[0].legend(loc='upper right', ncol=2)
ax[0].grid(True)

# Bottom Plot: Rectified Output Voltage
# We highlight the portion of the line voltages that form the DC envelope
ax[1].plot(t_deg, Vdc, color='orange', linewidth=2, label="Vdc (Output)")
ax[1].set_title("Rectified Output Voltage (6-Pulse Envelope)")
ax[1].grid(True)
ax[1].set_xlabel("Electrical Angle (degrees)")
ax[1].set_ylabel("Voltage (V)")

st.pyplot(fig)
