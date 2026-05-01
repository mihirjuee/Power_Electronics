# ============================================================
# 12-PULSE CONTROLLED RECTIFIER SIMULATOR (STREAMLIT)
# FINAL STABLE VERSION
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
# CALCULATION ENGINE
# ------------------------------------------------------------
Vm_phase = (V_ll_rms / np.sqrt(3)) * np.sqrt(2)
omega = 2 * np.pi * f

# Time base for 2 cycles
t = np.linspace(0, 2/f, 2000)

def get_6pulse_output(V_phase_max, ang_freq, time, alpha, phase_shift_deg=0):
    """Calculates the output of a 3-phase bridge rectifier."""
    shift = np.radians(phase_shift_deg)
    
    # Phase Voltages
    Va = V_phase_max * np.sin(ang_freq * time + shift)
    Vb = V_phase_max * np.sin(ang_freq * time - 2*np.pi/3 + shift)
    Vc = V_phase_max * np.sin(ang_freq * time - 4*np.pi/3 + shift)
    
    # Line-to-Line Voltages
    Vab = Va - Vb
    Vac = Va - Vc
    Vbc = Vb - Vc
    Vba = Vb - Va
    Vca = Vc - Va
    Vcb = Vc - Vb
    
    v_out = np.zeros_like(time)
    
    for i, t_val in enumerate(time):
        # Electrical angle relative to natural commutation point (30 degrees)
        theta = (ang_freq * t_val + shift) % (2 * np.pi)
        
        # Adjusting theta to align with the first commutation pulse
        # In a 3-phase bridge, natural commutation starts at 30 degrees (pi/6)
        phi = (theta - alpha - np.pi/6) % (2 * np.pi)
        sector = int(phi // (np.pi / 3))
        
        if sector == 0: v_out[i] = Vab[i]
        elif sector == 1: v_out[i] = Vac[i]
        elif sector == 2: v_out[i] = Vbc[i]
        elif sector == 3: v_out[i] = Vba[i]
        elif sector == 4: v_out[i] = Vca[i]
        else: v_out[i] = Vcb[i]
            
    return np.abs(v_out)

# Bridge 1 (Y-Y: 0° shift)
Vdc1 = get_6pulse_output(Vm_phase, omega, t, alpha_rad, 0)
# Bridge 2 (Y-Δ: 30° shift)
Vdc2 = get_6pulse_output(Vm_phase, omega, t, alpha_rad, 30)

# Total 12-Pulse Output (Average of series/parallel bridges)
Vdc_total = (Vdc1 + Vdc2) / 2

# ------------------------------------------------------------
# METRICS & PERFORMANCE
# ------------------------------------------------------------
v_avg = np.mean(Vdc_total)
i_avg = v_avg / R_load
v_rms = np.sqrt(np.mean(Vdc_total**2))
ripple_factor = np.sqrt((v_rms/v_avg)**2 - 1) if v_avg > 0 else 0

# Comparison to 6-pulse
v_avg_6 = np.mean(Vdc1)
v_rms_6 = np.sqrt(np.mean(Vdc1**2))
rf_6 = np.sqrt((v_rms_6/v_avg_6)**2 - 1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg DC Voltage", f"{v_avg:.2f} V")
col2.metric("Load Current", f"{i_avg:.2f} A")
col3.metric("Ripple Factor (12-P)", f"{ripple_factor:.4f}")
col4.metric("Ripple Improvement", f"{((rf_6 - ripple_factor)/rf_6)*100:.1f}%")

# ------------------------------------------------------------
# CIRCUIT DIAGRAM (MATPLOTLIB)
# ------------------------------------------------------------
st.subheader("🔌 System Architecture")
fig_ckt, ax_c = plt.subplots(figsize=(12, 4))
ax_c.set_xlim(0, 10); ax_c.set_ylim(0, 5); ax_c.axis('off')

# Schematic Drawing
ax_c.text(0.5, 2.5, "3Φ\nSource", bbox=dict(facecolor='none', shape='circle'))
ax_c.arrow(1, 2.5, 1, 0.8, head_width=0.1)
ax_c.arrow(1, 2.5, 1, -0.8, head_width=0.1)
ax_c.add_patch(Rectangle((2.2, 2.8), 1.5, 1, color='blue', alpha=0.3))
ax_c.text(2.95, 3.3, "Y-Y", ha='center')
ax_c.add_patch(Rectangle((2.2, 1.2), 1.5, 1, color='green', alpha=0.3))
ax_c.text(2.95, 1.7, "Y-Δ", ha='center')
ax_c.add_patch(Rectangle((4.5, 2.8), 1.5, 1, fill=False, lw=2))
ax_c.text(5.25, 3.3, "SCR 1", ha='center')
ax_c.add_patch(Rectangle((4.5, 1.2), 1.5, 1, fill=False, lw=2))
ax_c.text(5.25, 1.7, "SCR 2", ha='center')
ax_c.plot([6, 7.5, 7.5, 8.5], [3.3, 3.3, 2.5, 2.5], 'r')
ax_c.plot([6, 7.5, 7.5, 8.5], [1.7, 1.7, 2.5, 2.5], 'r')
ax_c.add_patch(Rectangle((8.5, 2.1), 1, 0.8, color='grey'))
ax_c.text(9, 2.5, "LOAD", ha='center', color='white')
st.pyplot(fig_ckt)

# ------------------------------------------------------------
# WAVEFORMS
# ------------------------------------------------------------
st.subheader("📈 Waveform Analysis")
fig, axs = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Subplot 1: Bridge Comparisons
axs[0].plot(t, Vdc1, 'b--', alpha=0.6, label="Bridge 1 (Y-Y)")
axs[0].plot(t, Vdc2, 'g--', alpha=0.6, label="Bridge 2 (Y-Δ)")
axs[0].set_title("Individual 6-Pulse Bridge Outputs")
axs[0].legend(loc='upper right')

# Subplot 2: Combined Output
axs[1].plot(t, Vdc_total, 'r', lw=2, label="12-Pulse Result")
axs[1].axhline(v_avg, color='black', linestyle=':', label="DC Mean")
axs[1].set_title("Final Rectified 12-Pulse Output")
axs[1].legend(loc='upper right')

# Subplot 3: Input Phases (Bridge 1)
Va_plt = Vm_phase * np.sin(omega * t)
Vb_plt = Vm_phase * np.sin(omega * t - 2*np.pi/3)
Vc_plt = Vm_phase * np.sin(omega * t - 4*np.pi/3)
axs[2].plot(t, Va_plt, label="Phase A")
axs[2].plot(t, Vb_plt, label="Phase B")
axs[2].plot(t, Vc_plt, label="Phase C")
axs[2].set_title("Input AC Supply (Phase-Neutral)")
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
with st.expander("📘 Detailed Engineering Concepts"):
    st.markdown(r"""
    ### 1. The 30° Phase Shift
    In a 12-pulse system, the primary goal is harmonic cancellation. By using a **Wye-Delta (Y-Δ)** transformer for the second bridge, we introduce a $30^\circ$ electrical phase shift. 
    
    ### 2. Harmonic Cancellation
    The Fourier series of a 6-pulse rectifier contains harmonics at $6n \pm 1$ (5th, 7th, 11th, 13th...). 
    * The $30^\circ$ shift causes the 5th and 7th harmonics of the two bridges to be $180^\circ$ out of phase.
    * When the outputs are combined, these harmonics **cancel out**.
    * The first significant harmonics remaining are the 11th and 13th ($12n \pm 1$).

    ### 3. Firing Angle ($\alpha$) Control
    The average DC output voltage is given by:
    $$V_{dc} = \frac{6V_{LL(peak)}}{\pi} \cos(\alpha)$$
    As you increase $\alpha$, the mean voltage decreases. In this 12-pulse simulation, the two bridges are assumed to be connected in a way that their voltages are averaged (parallel configuration with inter-phase transformer logic).
    """)

st.info("💡 **Pro-tip:** Set the Firing Angle to 0° and observe how the 12-pulse output becomes nearly flat compared to a standard 6-pulse bridge.")
