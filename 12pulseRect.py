# ============================================================
# 12-PULSE CONTROLLED RECTIFIER SIMULATOR (STREAMLIT)
# FINAL STABLE & OPTIMIZED VERSION
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
st.markdown("### Dual Converter System (Y-Y + Y-Δ Configuration)")

# ------------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------------
st.sidebar.header("Input Parameters")

V_ll_rms = st.sidebar.slider("Line-to-Line Voltage (V_rms)", 100, 1000, 415)
f = st.sidebar.slider("Frequency (Hz)", 25, 100, 50)
alpha_deg = st.sidebar.slider("Firing Angle α (°)", 0, 90, 15)
R_load = st.sidebar.slider("Load Resistance (Ω)", 1, 200, 10)

alpha_rad = np.radians(alpha_deg)

# ------------------------------------------------------------
# CALCULATION ENGINE (VECTORIZED)
# ------------------------------------------------------------
Vm_phase = (V_ll_rms / np.sqrt(3)) * np.sqrt(2)
omega = 2 * np.pi * f
t = np.linspace(0, 2/f, 3000)

def get_6pulse_output(V_p_max, ang_freq, time, alpha, shift_deg=0):
    shift = np.radians(shift_deg)
    
    # Phase Voltages
    Va = V_p_max * np.sin(ang_freq * time + shift)
    Vb = V_p_max * np.sin(ang_freq * time - 2*np.pi/3 + shift)
    Vc = V_p_max * np.sin(ang_freq * time - 4*np.pi/3 + shift)
    
    # Line Voltages
    v_line = {
        0: Va - Vb, # Vab
        1: Va - Vc, # Vac
        2: Vb - Vc, # Vbc
        3: Vb - Va, # Vba
        4: Vc - Va, # Vca
        5: Vc - Vb  # Vcb
    }
    
    # Logic: Identify which 60-degree sector we are in based on alpha
    # Natural commutation for Vab starts at 30 deg (pi/6)
    theta = (ang_freq * time + shift - alpha - np.pi/6) % (2 * np.pi)
    sector = (theta // (np.pi / 3)).astype(int) % 6
    
    # Vectorized selection
    v_out = np.choose(sector, [v_line[i] for i in range(6)])
    return np.abs(v_out)

# Generate bridge outputs
Vdc1 = get_6pulse_output(Vm_phase, omega, t, alpha_rad, 0)
Vdc2 = get_6pulse_output(Vm_phase, omega, t, alpha_rad, 30)
Vdc_total = (Vdc1 + Vdc2) / 2

# ------------------------------------------------------------
# PERFORMANCE METRICS
# ------------------------------------------------------------
v_avg = np.mean(Vdc_total)
i_avg = v_avg / R_load
v_rms = np.sqrt(np.mean(Vdc_total**2))
ripple_factor = np.sqrt(abs((v_rms/v_avg)**2 - 1)) if v_avg > 0 else 0

v_avg_6 = np.mean(Vdc1)
v_rms_6 = np.sqrt(np.mean(Vdc1**2))
rf_6 = np.sqrt(abs((v_rms_6/v_avg_6)**2 - 1))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg DC Voltage", f"{v_avg:.2f} V")
col2.metric("Load Current", f"{i_avg:.2f} A")
col3.metric("Ripple Factor (12-P)", f"{ripple_factor:.4f}")
col4.metric("Ripple Improvement", f"{((rf_6 - ripple_factor)/rf_6)*100:.1f}%" if rf_6 > 0 else "0%")

# ------------------------------------------------------------
# CIRCUIT DIAGRAM (FIXED BBOX ERROR)
# ------------------------------------------------------------
st.subheader("🔌 System Architecture")
fig_ckt, ax_c = plt.subplots(figsize=(12, 4))
ax_c.set_xlim(0, 10); ax_c.set_ylim(0, 5); ax_c.axis('off')

# Schematic Drawing - FIXED BBOX HERE
ax_c.text(0.5, 2.5, "3Φ\nSource", ha='center', va='center', 
          bbox=dict(facecolor='none', edgecolor='black', boxstyle='circle,pad=0.5'))

ax_c.annotate('', xy=(2.2, 3.3), xytext=(1.1, 2.7), arrowprops=dict(arrowstyle='->'))
ax_c.annotate('', xy=(2.2, 1.7), xytext=(1.1, 2.3), arrowprops=dict(arrowstyle='->'))

ax_c.add_patch(Rectangle((2.2, 2.8), 1.5, 1, color='blue', alpha=0.2))
ax_c.text(2.95, 3.3, "Y-Y (0°)", ha='center')
ax_c.add_patch(Rectangle((2.2, 1.2), 1.5, 1, color='green', alpha=0.2))
ax_c.text(2.95, 1.7, "Y-Δ (30°)", ha='center')

ax_c.add_patch(Rectangle((4.5, 2.8), 1.5, 1, fill=False, lw=1.5))
ax_c.text(5.25, 3.3, "6-Pulse Bridge 1", ha='center', fontsize=9)
ax_c.add_patch(Rectangle((4.5, 1.2), 1.5, 1, fill=False, lw=1.5))
ax_c.text(5.25, 1.7, "6-Pulse Bridge 2", ha='center', fontsize=9)

ax_c.plot([6, 7.5, 7.5, 8.5], [3.3, 3.3, 2.5, 2.5], 'r', lw=2)
ax_c.plot([6, 7.5, 7.5, 8.5], [1.7, 1.7, 2.5, 2.5], 'r', lw=2)
ax_c.add_patch(Rectangle((8.5, 2.0), 1.2, 1.0, color='#333333'))
ax_c.text(9.1, 2.5, "LOAD", ha='center', va='center', color='white', fontweight='bold')

st.pyplot(fig_ckt)

# ------------------------------------------------------------
# WAVEFORMS
# ------------------------------------------------------------
st.subheader("📈 Waveform Analysis")
fig, axs = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Subplot 1: Bridges
axs[0].plot(t, Vdc1, 'b--', alpha=0.5, label="Bridge 1 (0°)")
axs[0].plot(t, Vdc2, 'g--', alpha=0.5, label="Bridge 2 (30°)")
axs[0].set_title("Individual Bridge Voltages")
axs[0].legend(loc='upper right')

# Subplot 2: Total
axs[1].plot(t, Vdc_total, 'r', lw=2, label="12-Pulse Output")
axs[1].axhline(v_avg, color='black', linestyle=':', label="Average Vdc")
axs[1].set_title("Combined DC Output Voltage")
axs[1].legend(loc='upper right')

# Subplot 3: AC Input
Va_p = Vm_phase * np.sin(omega * t)
Vb_p = Vm_phase * np.sin(omega * t - 2*np.pi/3)
Vc_p = Vm_phase * np.sin(omega * t - 4*np.pi/3)
axs[2].plot(t, Va_p, label="Phase A")
axs[2].plot(t, Vb_p, label="Phase B")
axs[2].plot(t, Vc_p, label="Phase C")
axs[2].set_title("Input AC Supply (Phase-to-Neutral)")
axs[2].legend(loc='upper right')

for ax in axs:
    ax.grid(True, alpha=0.3)
    ax.set_ylabel("Voltage (V)")
axs[2].set_xlabel("Time (s)")

plt.tight_layout()
st.pyplot(fig)

# ------------------------------------------------------------
# THEORY
# ------------------------------------------------------------
with st.expander("📘 Engineering Theory"):
    st.markdown(r"""
    ### 1. Harmonic Cancellation
    In a 12-pulse rectifier, the $30^\circ$ phase shift provided by the Delta-Wye transformer causes the 5th and 7th harmonics of the two bridges to be exactly $180^\circ$ out of phase. When summed, they cancel out, leaving the 11th and 13th as the primary harmonics.

    ### 2. Output Voltage Calculation
    The average output voltage for a controlled 12-pulse rectifier is:
    $$V_{dc} = \frac{6V_{LL(peak)}}{\pi} \cos(\alpha)$$
    Where $V_{LL(peak)} = V_{rms} \times \sqrt{2}$.

    ### 3. Ripple Factor
    The ripple factor for a 12-pulse rectifier is approximately **0.011 (1.1%)** at $\alpha=0$, compared to **0.042 (4.2%)** for a 6-pulse rectifier.
    """)

st.info("⚙️ **Virtual Lab Note:** Adjust the Firing Angle $\alpha$ to see how the conduction sectors shift in the waveforms above.")
