# ============================================================
# 12-PULSE CONTROLLED RECTIFIER SIMULATOR (STREAMLIT)
# UPDATED:
# ✅ Added transformer + dual bridge circuit diagram
# ✅ Y-Y + Y-Δ representation
# ✅ 30° phase shift
# ✅ Full virtual lab dashboard
# ============================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="12-Pulse Rectifier Simulator", layout="wide")

st.title("⚡ 12-Pulse Controlled Rectifier Virtual Lab")
st.markdown("### Y-Y + Y-Δ Dual Converter System")

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.header("Input Parameters")

V_ll = st.sidebar.slider("Line-Line Voltage (V)", 100, 1000, 415)
f = st.sidebar.slider("Frequency (Hz)", 25, 100, 50)
alpha_deg = st.sidebar.slider("Firing Angle α (°)", 0, 90, 30)
R_load = st.sidebar.slider("Load Resistance (Ω)", 1, 100, 10)

alpha = np.radians(alpha_deg)

# ------------------------------------------------------------
# SOURCE CALCULATIONS
# ------------------------------------------------------------
Vm_phase = (V_ll / np.sqrt(3)) * np.sqrt(2)
omega = 2 * np.pi * f

t = np.linspace(0, 0.04, 5000)

# Main source
Va = Vm_phase * np.sin(omega * t)
Vb = Vm_phase * np.sin(omega * t - 2*np.pi/3)
Vc = Vm_phase * np.sin(omega * t - 4*np.pi/3)

# Delta shifted source
shift = np.radians(30)
Va2 = Vm_phase * np.sin(omega * t + shift)
Vb2 = Vm_phase * np.sin(omega * t - 2*np.pi/3 + shift)
Vc2 = Vm_phase * np.sin(omega * t - 4*np.pi/3 + shift)

# ------------------------------------------------------------
# RECTIFIER MODEL
# ------------------------------------------------------------
def six_pulse(Va, Vb, Vc, alpha):
    Vout = np.zeros_like(Va)

    for i in range(len(Va)):
        vmax = max(Va[i], Vb[i], Vc[i])
        vmin = min(Va[i], Vb[i], Vc[i])

        angle = (omega * t[i]) % (2*np.pi)

        if angle >= alpha:
            Vout[i] = vmax - vmin
        else:
            Vout[i] = 0

    return Vout

Vdc1 = six_pulse(Va, Vb, Vc, alpha)
Vdc2 = six_pulse(Va2, Vb2, Vc2, alpha)

Vdc_total = (Vdc1 + Vdc2) / 2

# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------
Vdc_avg = np.mean(Vdc_total)
Idc = Vdc_avg / R_load
Vr_rms = np.sqrt(np.mean((Vdc_total - Vdc_avg)**2))
ripple = Vr_rms / Vdc_avg if Vdc_avg > 0 else 0

# ------------------------------------------------------------
# CIRCUIT DIAGRAM
# ------------------------------------------------------------
st.subheader("🔌 12-Pulse Rectifier Circuit Diagram")

fig_circuit, ax = plt.subplots(figsize=(16, 7))
ax.set_xlim(0, 20)
ax.set_ylim(0, 12)
ax.axis("off")

# AC Source
ax.text(1, 10, "3Φ AC\nSupply", fontsize=12, ha='center')
ax.plot([2, 4], [10, 10], 'k', lw=2)

# Transformer
ax.add_patch(Rectangle((4, 8.5), 2, 3, fill=False, lw=2))
ax.text(5, 10, "Transformer", ha='center')

# Y-Y output
ax.plot([6, 9], [10.5, 10.5], 'b', lw=2)
ax.text(7.5, 11, "Y-Y", color='blue')

# Y-Δ output
ax.plot([6, 9], [9, 9], 'g', lw=2)
ax.text(7.5, 8.3, "Y-Δ (30°)", color='green')

# Bridge 1
ax.add_patch(Rectangle((9, 9.8), 3, 1.5, fill=False, lw=2))
ax.text(10.5, 10.55, "6-Pulse\nBridge-1", ha='center')

# Bridge 2
ax.add_patch(Rectangle((9, 8.3), 3, 1.5, fill=False, lw=2))
ax.text(10.5, 9.05, "6-Pulse\nBridge-2", ha='center')

# Combined DC bus
ax.plot([12, 15], [10.5, 10.5], 'r', lw=2)
ax.plot([12, 15], [9.0, 9.0], 'r', lw=2)
ax.plot([15, 15], [9.0, 10.5], 'r', lw=2)

# Load
ax.add_patch(Rectangle((16, 8.8), 2, 2, fill=False, lw=2))
ax.text(17, 9.8, "R Load", ha='center')

ax.plot([15, 16], [9.75, 9.75], 'k', lw=2)

# Output
ax.text(18.8, 9.75, "+ Vdc", fontsize=12)

plt.tight_layout()
st.pyplot(fig_circuit)

# ------------------------------------------------------------
# PERFORMANCE
# ------------------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Average DC Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Load Current", f"{Idc:.2f} A")
col3.metric("Ripple Factor", f"{ripple:.4f}")

# ------------------------------------------------------------
# WAVEFORMS
# ------------------------------------------------------------
st.subheader("📈 Waveforms")

fig, axs = plt.subplots(4, 1, figsize=(14, 16))

# AC
axs[0].plot(t, Va, label='Va')
axs[0].plot(t, Vb, label='Vb')
axs[0].plot(t, Vc, label='Vc')
axs[0].set_title("3-Phase Input")
axs[0].legend()
axs[0].grid()

# Bridge1
axs[1].plot(t, Vdc1)
axs[1].set_title("Bridge-1 Output (Y-Y)")
axs[1].grid()

# Bridge2
axs[2].plot(t, Vdc2)
axs[2].set_title("Bridge-2 Output (Y-Δ)")
axs[2].grid()

# Final
axs[3].plot(t, Vdc_total, color='red')
axs[3].axhline(Vdc_avg, linestyle='--')
axs[3].set_title("Combined 12-Pulse Output")
axs[3].grid()

plt.tight_layout()
st.pyplot(fig)

# ------------------------------------------------------------
# THEORY
# ------------------------------------------------------------
with st.expander("📘 Working Principle"):
    st.markdown("""
    ## 12-Pulse Rectifier:
    Two 6-pulse bridges are fed from:
    
    ### Bridge 1:
    Y-Y transformer secondary
    
    ### Bridge 2:
    Y-Δ transformer secondary (30° phase shift)
    
    The phase shift cancels lower harmonics:
    ✅ 5th  
    ✅ 7th  
    
    ### Advantages:
    - Lower THD
    - Reduced ripple
    - Better DC quality
    - Used in HVDC, large DC drives
    """)

st.markdown("---")
st.markdown("⚙️ Power Electronics Virtual Lab")
