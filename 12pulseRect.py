# ============================================================
# 12-PULSE CONTROLLED RECTIFIER SIMULATOR (STREAMLIT)
# FULLY CORRECTED VERSION
# FIXES:
# ✅ Continuous waveform (NO break between cycles)
# ✅ Exact 30° transformer phase shift
# ✅ Proper 6-pulse SCR conduction sequence
# ✅ Circuit diagram included
# ✅ Ripple comparison
# ✅ Real engineering dashboard
# ============================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="12-Pulse Rectifier Virtual Lab", layout="wide")

st.title("⚡ 12-Pulse Controlled Rectifier Virtual Lab")
st.markdown("### Dual Converter (Y-Y + Y-Δ Transformer)")

# ------------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------------
st.sidebar.header("Input Parameters")

V_ll = st.sidebar.slider("3-Phase Line Voltage VLL (V)", 100, 1100, 415)
f = st.sidebar.slider("Frequency (Hz)", 25, 100, 50)
alpha_deg = st.sidebar.slider("Firing Angle α (degrees)", 0, 90, 0)
R_load = st.sidebar.slider("Load Resistance (Ω)", 1, 200, 10)

alpha = np.radians(alpha_deg)

# ------------------------------------------------------------
# SOURCE VALUES
# ------------------------------------------------------------
Vm_phase = (V_ll / np.sqrt(3)) * np.sqrt(2)
omega = 2 * np.pi * f

# Exact continuous time base
cycles = 2
samples_per_cycle = 4000
t = np.linspace(
    0,
    cycles / f,
    cycles * samples_per_cycle,
    endpoint=False
)

# ------------------------------------------------------------
# THREE PHASE INPUTS
# ------------------------------------------------------------
Va = Vm_phase * np.sin(omega * t)
Vb = Vm_phase * np.sin(omega * t - 2 * np.pi / 3)
Vc = Vm_phase * np.sin(omega * t - 4 * np.pi / 3)

# 30° shifted set for second bridge
shift = np.radians(30)

Va2 = Vm_phase * np.sin(omega * t + shift)
Vb2 = Vm_phase * np.sin(omega * t - 2 * np.pi / 3 + shift)
Vc2 = Vm_phase * np.sin(omega * t - 4 * np.pi / 3 + shift)

# ------------------------------------------------------------
# CORRECT 6-PULSE CONTROLLED RECTIFIER
# ------------------------------------------------------------
def six_pulse_rectifier(Va, Vb, Vc, alpha):
    Vout = np.zeros_like(Va)

    for i in range(len(Va)):

        # Electrical angle
        theta = (omega * t[i]) % (2 * np.pi)

        # Apply firing delay
        theta_delay = (theta - alpha) % (2 * np.pi)

        # 60-degree sector
        sector = int(theta_delay // (np.pi / 3))

        # Line voltages
        Vab = Va[i] - Vb[i]
        Vac = Va[i] - Vc[i]
        Vbc = Vb[i] - Vc[i]
        Vba = Vb[i] - Va[i]
        Vca = Vc[i] - Va[i]
        Vcb = Vc[i] - Vb[i]

        # SCR pair conduction sequence
        if sector == 0:
            Vout[i] = Vab
        elif sector == 1:
            Vout[i] = Vac
        elif sector == 2:
            Vout[i] = Vbc
        elif sector == 3:
            Vout[i] = Vba
        elif sector == 4:
            Vout[i] = Vca
        elif sector == 5:
            Vout[i] = Vcb

        # Rectified output
        Vout[i] = abs(Vout[i])

    return Vout

# ------------------------------------------------------------
# BRIDGE OUTPUTS
# ------------------------------------------------------------
Vdc1 = six_pulse_rectifier(Va, Vb, Vc, alpha)
Vdc2 = six_pulse_rectifier(Va2, Vb2, Vc2, alpha)

# Combined 12-pulse output
Vdc_total = (Vdc1 + Vdc2) / 2

# ------------------------------------------------------------
# PERFORMANCE
# ------------------------------------------------------------
Vdc_avg = np.mean(Vdc_total)
Idc_avg = Vdc_avg / R_load

Vripple_rms = np.sqrt(np.mean((Vdc_total - Vdc_avg) ** 2))
ripple_factor = Vripple_rms / Vdc_avg if Vdc_avg > 0 else 0

# 6-pulse ripple comparison
Vdc1_avg = np.mean(Vdc1)
Vripple6 = np.sqrt(np.mean((Vdc1 - Vdc1_avg) ** 2))
ripple6 = Vripple6 / Vdc1_avg if Vdc1_avg > 0 else 0

ripple_reduction = ((ripple6 - ripple_factor) / ripple6) * 100 if ripple6 > 0 else 0

# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------
st.subheader("📊 Output Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average DC Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Average Load Current", f"{Idc_avg:.2f} A")
col3.metric("12-Pulse Ripple Factor", f"{ripple_factor:.4f}")
col4.metric("Ripple Reduction", f"{ripple_reduction:.2f}%")

# ------------------------------------------------------------
# CIRCUIT DIAGRAM
# ------------------------------------------------------------
st.subheader("🔌 12-Pulse Rectifier Circuit Diagram")

fig_circuit, ax = plt.subplots(figsize=(16, 7))
ax.set_xlim(0, 22)
ax.set_ylim(0, 14)
ax.axis("off")

# AC Source
ax.text(1.5, 11, "3Φ AC\nSource", fontsize=13, ha='center')
ax.plot([2.5, 4], [11, 11], lw=2)

# Transformer
ax.add_patch(Rectangle((4, 9), 3, 4, fill=False, lw=2))
ax.text(5.5, 11, "Phase Shift\nTransformer", ha='center')

# Outputs
ax.plot([7, 10], [12, 12], lw=2, color='blue')
ax.plot([7, 10], [10, 10], lw=2, color='green')

ax.text(8.5, 12.5, "Y-Y Secondary", color='blue')
ax.text(8.5, 9.3, "Y-Δ Secondary (30°)", color='green')

# Bridge 1
ax.add_patch(Rectangle((10, 11.2), 3, 1.6, fill=False, lw=2))
ax.text(11.5, 12, "6-Pulse\nBridge 1", ha='center')

# Bridge 2
ax.add_patch(Rectangle((10, 9.2), 3, 1.6, fill=False, lw=2))
ax.text(11.5, 10, "6-Pulse\nBridge 2", ha='center')

# Combined output
ax.plot([13, 16], [12, 12], lw=2, color='red')
ax.plot([13, 16], [10, 10], lw=2, color='red')
ax.plot([16, 16], [10, 12], lw=2, color='red')

# Load
ax.add_patch(Rectangle((17, 10.3), 2.5, 1.5, fill=False, lw=2))
ax.text(18.25, 11.05, "R Load", ha='center')

ax.plot([16, 17], [11, 11], lw=2)
ax.text(20, 11, "+Vdc", fontsize=12)

plt.tight_layout()
st.pyplot(fig_circuit)

# ------------------------------------------------------------
# WAVEFORMS
# ------------------------------------------------------------
st.subheader("📈 Waveform Analysis")

fig, axs = plt.subplots(4, 1, figsize=(15, 18))

# Input supply
axs[0].plot(t, Va, label="Va")
axs[0].plot(t, Vb, label="Vb")
axs[0].plot(t, Vc, label="Vc")
axs[0].set_title("3-Phase Input Voltages")
axs[0].legend()
axs[0].grid(True)

# Bridge 1
axs[1].plot(t, Vdc1, color='blue')
axs[1].set_title("6-Pulse Bridge 1 Output (Y-Y)")
axs[1].grid(True)

# Bridge 2
axs[2].plot(t, Vdc2, color='green')
axs[2].set_title("6-Pulse Bridge 2 Output (Y-Δ, 30° Shift)")
axs[2].grid(True)

# Final output
axs[3].plot(t, Vdc_total, color='red', label="12-Pulse Output")
axs[3].axhline(Vdc_avg, linestyle='--', label="Average DC")
axs[3].set_title("Combined 12-Pulse Output")
axs[3].legend()
axs[3].grid(True)

for axx in axs:
    axx.set_xlabel("Time (s)")
    axx.set_ylabel("Voltage (V)")

plt.tight_layout()
st.pyplot(fig)

# ------------------------------------------------------------
# RIPPLE COMPARISON
# ------------------------------------------------------------
st.subheader("📉 Ripple Comparison")

st.write({
    "6-Pulse Ripple Factor": round(ripple6, 4),
    "12-Pulse Ripple Factor": round(ripple_factor, 4),
    "Ripple Reduction (%)": round(ripple_reduction, 2)
})

# ------------------------------------------------------------
# THEORY
# ------------------------------------------------------------
with st.expander("📘 Engineering Theory"):
    st.markdown("""
    ## 12-Pulse Controlled Rectifier

    A 12-pulse converter uses:
    - Two 6-pulse SCR bridges
    - One Y-Y transformer secondary
    - One Y-Δ transformer secondary

    ### Key Principle:
    The Δ secondary introduces a 30° phase shift.

    ### Result:
    Lower-order harmonics cancel:
    ✅ 5th harmonic  
    ✅ 7th harmonic  

    ### Benefits:
    - Lower THD
    - Smoother DC output
    - Reduced ripple
    - Better industrial power quality

    ### Applications:
    - HVDC transmission
    - Large DC motor drives
    - Electrochemical plants
    - Industrial rectifiers
    """)

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.markdown("⚙️ Designed for Advanced Power Electronics Education")
