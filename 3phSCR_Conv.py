# ======================================================================
# 3-PHASE FULLY CONTROLLED RECTIFIER (6-SCR / 6-PULSE) - STREAMLIT APP
# Converts your uncontrolled rectifier into controlled rectifier
# Added:
# ✅ Firing angle alpha control
# ✅ SCR conduction sequence
# ✅ Controlled output waveform
# ✅ Avg output formula Vdc = 1.35*VLL*cos(alpha)
# ✅ Detailed waveform + conduction labels
# ======================================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import io
from PIL import Image

# ================= PAGE =================
st.set_page_config(page_title="3-Phase Controlled Rectifier",page_icon="logo.png", layout="wide")
st.title("⚡ 3-Phase Fully Controlled Rectifier (6-SCR Converter)")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Input Parameters")
V_ll = st.sidebar.slider("Line Voltage V_LL (RMS)", 100, 500, 400)
f = st.sidebar.slider("Frequency (Hz)", 25, 60, 50)
R_load = st.sidebar.slider("Load Resistance (Ω)", 10, 500, 100)
alpha_deg = st.sidebar.slider("Firing Angle α (degrees)", 0, 150, 30)

# ================= BASIC CALCULATIONS =================
alpha = np.radians(alpha_deg)

Vm = np.sqrt(2) * (V_ll / np.sqrt(3))
t = np.linspace(0, 2 * np.pi, 2000)

# Phase Voltages
Va = Vm * np.sin(t)
Vb = Vm * np.sin(t - 2*np.pi/3)
Vc = Vm * np.sin(t - 4*np.pi/3)

# Line-Line Voltages
Vab = Va - Vb
Vac = Va - Vc
Vbc = Vb - Vc
Vba = Vb - Va
Vca = Vc - Va
Vcb = Vc - Vb

line_voltages = [Vab, Vac, Vbc, Vba, Vca, Vcb]
line_labels = ['ab', 'ac', 'bc', 'ba', 'ca', 'cb']
scr_labels = ['T1,T6', 'T1,T2', 'T3,T2', 'T3,T4', 'T5,T4', 'T5,T6']

# ================= CONTROLLED OUTPUT =================
Vdc = np.zeros_like(t)

# SCR firing begins at π/6 + α
start_angle = np.pi/6 + alpha
interval = np.pi / 3

for i in range(6):
    t_start = start_angle + i * interval
    t_end = t_start + interval
    mask = (t >= t_start) & (t < t_end)

    if i < len(line_voltages):
        Vdc[mask] = line_voltages[i][mask]

# Wrap around for continuity
for i in range(6):
    t_start = start_angle + i * interval - 2*np.pi
    t_end = t_start + interval
    mask = (t >= t_start) & (t < t_end)

    if i < len(line_voltages):
        Vdc[mask] = line_voltages[i][mask]

# Average DC
Vdc_avg = 1.35 * V_ll * np.cos(alpha)
Idc_avg = Vdc_avg / R_load
P_out = Vdc_avg * Idc_avg

# ================= CIRCUIT DIAGRAM =================
st.subheader("🔌 Circuit Diagram")

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
    D1 = d.add(elm.SCR().up(2).label("T1"))
    d += elm.Line().up(0.5)
    d.push()
    d += elm.Line().at(S2.end).right(2)
    d.push()
    d += elm.Dot()
    d += elm.Line().up(2)
    D3 = d.add(elm.SCR().up().label("T3"))
    #d += elm.Line().up(0.25)
    d += elm.Line().at(S3.end).right(3.5)
    d.push()
    d += elm.Dot()
    D5 = d.add(elm.SCR().up().label("T5"))
    d.pop()
    d += elm.Line().down(4)
    D2 = d.add(elm.SCR().down().reverse().label("T2"))
    #d += elm.Line().down(0.5)
    # ================= BOTTOM DIODES =================
    D4 = d.add(elm.SCR().at(S1.end).down().reverse().label("T4"))
    d.pop()
    d += elm.Line().down(2)
    D6 = d.add(elm.SCR().down().reverse().label("T6"))
    d += elm.Line().at(S3.end).right(1)
    

    # ================= DC BUS (TOP) =================
    d.pop()
    d += elm.Line().right(2)
    d += elm.Line().to(D5.end)

    # ================= LOAD =================
    d += elm.Line().right(2)
    d += elm.Line().down(3.5)
    R = d.add(elm.Resistor().down().label(f"R={R_load}$\Omega$"))
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





# ================= WAVEFORMS =================
st.subheader("📊 Waveform Analysis")

fig, ax = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# -------- TOP: Source Voltages --------
ax[0].plot(t, Va, label='Va', color='r')
ax[0].plot(t, Vb, label='Vb', color='g')
ax[0].plot(t, Vc, label='Vc', color='b')

ax[0].set_title("3-Phase Source Voltages")
ax[0].set_ylabel("Voltage (V)")
ax[0].grid(True, linestyle='--', alpha=0.5)
ax[0].legend()

# -------- BOTTOM: Controlled Output --------
for lv in line_voltages:
    ax[1].plot(t, lv, linestyle=':', alpha=0.2, color='gray')

ax[1].plot(t, Vdc, color='black', linewidth=2.5, label='Controlled Vdc')

# Firing markers
for i in range(6):
    fire_angle = start_angle + i * interval
    if fire_angle <= 2*np.pi:
        ax[1].axvline(fire_angle, color='red', linestyle='--', alpha=0.7)

        # Label
        idx = np.argmin(np.abs(t - fire_angle))
        ax[1].text(
            fire_angle,
            Vdc[idx] - 30,
            f"{line_labels[i]}\n{scr_labels[i]}",
            ha='center',
            fontsize=9,
            fontweight='bold'
        )

ax[1].set_title(f"Controlled Output Voltage (α = {alpha_deg}°)")
ax[1].set_ylabel("Vdc (V)")
ax[1].set_xlabel("Electrical Angle ωt")

xticks = [0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3, 2*np.pi]
xticklabels = ['0', 'π/3', '2π/3', 'π', '4π/3', '5π/3', '2π']
ax[1].set_xticks(xticks)
ax[1].set_xticklabels(xticklabels)

ax[1].grid(True, linestyle='--', alpha=0.5)
ax[1].legend()

plt.tight_layout()
st.pyplot(fig)

# ================= METRICS =================
st.subheader("📈 Performance Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Average DC Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Average DC Current", f"{Idc_avg:.2f} A")
col3.metric("Output Power", f"{P_out/1000:.2f} kW")

# ================= MODE =================
if alpha_deg < 90:
    st.success("⚡ Rectifier Mode (Positive Average Output)")
elif alpha_deg == 90:
    st.warning("⚠ Boundary Mode (Vdc ≈ 0)")
else:
    st.error("🔋 Inverter Region (Negative Average Output possible with active load)")

# ================= FORMULAS =================
st.markdown("---")
st.subheader("📜 Key Equations")

st.latex(r"V_{dc(avg)} = 1.35 \times V_{LL} \cos(\alpha)")
st.latex(r"I_{dc(avg)} = \frac{V_{dc}}{R}")
st.latex(r"P_{out} = V_{dc} \cdot I_{dc}")

st.info("""
📘 Notes:
• α = 0° → behaves like diode rectifier  
• α < 90° → rectification mode  
• α > 90° → inverter mode possible (with suitable DC source/load)  
• Each SCR pair conducts for 60°
""")
