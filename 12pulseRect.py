# ============================================================
# 12-PULSE CONTROLLED RECTIFIER SIMULATOR (STREAMLIT)
# Author: OpenAI
# Features:
# ✅ Dual 6-pulse bridges (Y-Y and Y-Δ)
# ✅ 30° phase shift
# ✅ Adjustable firing angle
# ✅ Ripple reduction visualization
# ✅ Average DC voltage
# ✅ Ripple factor
# ✅ Real lab-style dashboard
# ============================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="12-Pulse Rectifier Simulator", layout="wide")

st.title("⚡ 12-Pulse Controlled Rectifier Virtual Lab")
st.markdown("### Dual 6-Pulse Bridge (Y-Y + Y-Δ Transformer Configuration)")

# ------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------
st.sidebar.header("Input Parameters")

V_ll = st.sidebar.slider("AC Line-Line Voltage (V)", 100, 1000, 415)
f = st.sidebar.slider("Frequency (Hz)", 25, 100, 50)
alpha_deg = st.sidebar.slider("Firing Angle α (degrees)", 0, 90, 30)
R_load = st.sidebar.slider("Load Resistance (Ω)", 1, 100, 10)

# ------------------------------------------------------------
# BASIC CALCULATIONS
# ------------------------------------------------------------
alpha = np.radians(alpha_deg)
Vm_phase = (V_ll / np.sqrt(3)) * np.sqrt(2)
omega = 2 * np.pi * f

# Time base
t = np.linspace(0, 0.04, 5000)   # 2 cycles at 50Hz

# ------------------------------------------------------------
# 3-PHASE SOURCE VOLTAGES
# ------------------------------------------------------------
Va = Vm_phase * np.sin(omega * t)
Vb = Vm_phase * np.sin(omega * t - 2*np.pi/3)
Vc = Vm_phase * np.sin(omega * t - 4*np.pi/3)

# Delta shifted source (30°)
shift = np.radians(30)

Va_shift = Vm_phase * np.sin(omega * t + shift)
Vb_shift = Vm_phase * np.sin(omega * t - 2*np.pi/3 + shift)
Vc_shift = Vm_phase * np.sin(omega * t - 4*np.pi/3 + shift)

# ------------------------------------------------------------
# RECTIFIER FUNCTION
# ------------------------------------------------------------
def six_pulse_output(Va, Vb, Vc, alpha):
    Vout = np.zeros_like(Va)

    for i in range(len(Va)):
        phase_voltages = np.array([Va[i], Vb[i], Vc[i]])
        vmax = np.max(phase_voltages)
        vmin = np.min(phase_voltages)

        # Controlled conduction approximation
        angle = (omega * t[i]) % (2*np.pi)

        if angle >= alpha:
            Vout[i] = vmax - vmin
        else:
            Vout[i] = 0

    return Vout

# ------------------------------------------------------------
# BRIDGE OUTPUTS
# ------------------------------------------------------------
Vdc_bridge1 = six_pulse_output(Va, Vb, Vc, alpha)
Vdc_bridge2 = six_pulse_output(Va_shift, Vb_shift, Vc_shift, alpha)

# Combined 12-pulse
Vdc_total = (Vdc_bridge1 + Vdc_bridge2) / 2

# ------------------------------------------------------------
# PERFORMANCE METRICS
# ------------------------------------------------------------
Vdc_avg = np.mean(Vdc_total)
Idc_avg = Vdc_avg / R_load

Vripple_rms = np.sqrt(np.mean((Vdc_total - Vdc_avg)**2))
ripple_factor = Vripple_rms / Vdc_avg if Vdc_avg != 0 else 0

# Theoretical
Vdc_theoretical = 2 * (3 * np.sqrt(2) / np.pi) * (V_ll/np.sqrt(3)) * np.cos(alpha)

# ------------------------------------------------------------
# DISPLAY METRICS
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average DC Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Load Current", f"{Idc_avg:.2f} A")
col3.metric("Ripple Factor", f"{ripple_factor:.4f}")
col4.metric("Theoretical Vdc", f"{Vdc_theoretical:.2f} V")

# ------------------------------------------------------------
# PLOTS
# ------------------------------------------------------------
fig, axs = plt.subplots(4, 1, figsize=(14, 16))

# Supply voltages
axs[0].plot(t, Va, label="Va")
axs[0].plot(t, Vb, label="Vb")
axs[0].plot(t, Vc, label="Vc")
axs[0].set_title("3-Phase Supply Voltages")
axs[0].set_ylabel("Voltage (V)")
axs[0].legend()
axs[0].grid(True)

# Bridge 1
axs[1].plot(t, Vdc_bridge1, color='blue')
axs[1].set_title("6-Pulse Bridge 1 Output (Y-Y)")
axs[1].set_ylabel("Voltage (V)")
axs[1].grid(True)

# Bridge 2
axs[2].plot(t, Vdc_bridge2, color='green')
axs[2].set_title("6-Pulse Bridge 2 Output (Y-Δ, 30° Shift)")
axs[2].set_ylabel("Voltage (V)")
axs[2].grid(True)

# Final 12-pulse
axs[3].plot(t, Vdc_total, color='red')
axs[3].axhline(Vdc_avg, linestyle="--", label="Average DC")
axs[3].set_title("Combined 12-Pulse Rectifier Output")
axs[3].set_xlabel("Time (s)")
axs[3].set_ylabel("Voltage (V)")
axs[3].legend()
axs[3].grid(True)

plt.tight_layout()
st.pyplot(fig)

# ------------------------------------------------------------
# HARMONIC / RIPPLE COMPARISON
# ------------------------------------------------------------
st.subheader("📉 Ripple Reduction Analysis")

ripple_6pulse = np.sqrt(np.mean((Vdc_bridge1 - np.mean(Vdc_bridge1))**2)) / np.mean(Vdc_bridge1)

comparison = {
    "6-Pulse Ripple Factor": ripple_6pulse,
    "12-Pulse Ripple Factor": ripple_factor,
    "Ripple Reduction (%)": ((ripple_6pulse - ripple_factor) / ripple_6pulse) * 100 if ripple_6pulse != 0 else 0
}

st.write(comparison)

# ------------------------------------------------------------
# THEORY SECTION
# ------------------------------------------------------------
with st.expander("📘 Engineering Theory"):
    st.markdown("""
    ### 12-Pulse Rectifier Principle:
    A 12-pulse rectifier uses:
    - Two 6-pulse bridges
    - One fed from Y-Y transformer
    - One fed from Y-Δ transformer
    
    The Δ transformer introduces **30° phase shift**, reducing:
    - 5th harmonic
    - 7th harmonic
    - Ripple
    
    ### Average Output Voltage:
    Vdc = 2 × (3√2 / π) × V_phase × cos(α)
    
    ### Benefits:
    ✅ Lower THD  
    ✅ Smoother DC  
    ✅ Better power quality  
    ✅ Industrial drives & HVDC applications  
    """)

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.markdown("⚙️ Designed for Power Electronics Education | 12-Pulse Controlled Converter")
