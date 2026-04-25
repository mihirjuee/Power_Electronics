import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import time

# ================= PAGE =================
st.set_page_config(page_title="SCR Converter Animation", layout="wide")
st.title("⚡ Single-Phase SCR Full Converter (Animated)")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Controls")

Vm = st.sidebar.number_input("Peak Voltage (V)", value=325.0)
f = st.sidebar.number_input("Frequency (Hz)", value=50.0)
alpha_deg = st.sidebar.slider("Firing Angle α (deg)", 0, 180, 60)

run = st.sidebar.button("▶️ Start Animation")

alpha = np.deg2rad(alpha_deg)
w = 2 * np.pi * f

t = np.linspace(0, 2*np.pi, 200)

# ================= PLACEHOLDERS =================
circuit_placeholder = st.empty()
wave_placeholder = st.empty()

# ================= DRAW CIRCUIT =================
def draw_circuit(active_pair):
    with schemdraw.Drawing() as d:

        # AC Source
        d += elm.SourceSin().label("AC")

        d += elm.Line().right()

        # Top branch SCRs
        color1 = "red" if active_pair == "T1T2" else "black"
        color2 = "red" if active_pair == "T3T4" else "black"

        d.push()
        d += elm.SCR().right().label("T1").color(color1)
        d += elm.Line().right()
        d += elm.Resistor().down().label("Load")
        d += elm.Line().left()
        d += elm.SCR().left().label("T2").color(color1)
        d.pop()

        # Bottom branch SCRs
        d.push()
        d += elm.SCR().down().label("T3").color(color2)
        d += elm.Line().down()
        d += elm.SCR().up().label("T4").color(color2)
        d.pop()

        return d.draw().fig

# ================= ANIMATION =================
if run:

    theta_all = np.linspace(0, 2*np.pi, len(t))
    theta_deg_all = np.degrees(theta_all)

    vin = Vm * np.sin(theta_all)
    vout = np.zeros_like(vin)
    iout = np.zeros_like(vin)

    for i in range(len(theta_all)):

        theta = theta_all[i]

        # ================= CONDUCTION =================
        if alpha <= theta <= np.pi:
            pair = "T1T2"
            color = "red"
            vout[i] = Vm * np.sin(theta)

        elif np.pi + alpha <= theta <= 2*np.pi:
            pair = "T3T4"
            color = "blue"
            vout[i] = Vm * np.sin(theta)

        else:
            pair = "NONE"
            color = "gray"
            vout[i] = 0

        iout[i] = vout[i] / R

        # ================= CIRCUIT =================
        fig1 = draw_circuit(pair)
        circuit_placeholder.pyplot(fig1)

        # ================= WAVEFORMS =================
        fig2, ax = plt.subplots(3, 1, figsize=(9, 6))

        # Input voltage
        ax[0].plot(theta_deg_all[:i+1], vin[:i+1])
        ax[0].axvline(alpha_deg, linestyle='--', color='red')
        ax[0].axvline(180 + alpha_deg, linestyle='--', color='blue')
        ax[0].set_title("Input Voltage")
        ax[0].grid()

        # Output voltage
        ax[1].plot(theta_deg_all[:i+1], vout[:i+1], color=color)
        ax[1].set_title("Output Voltage")
        ax[1].grid()

        # Current
        ax[2].plot(theta_deg_all[:i+1], iout[:i+1], color=color)
        ax[2].set_title("Load Current")
        ax[2].set_xlabel("Angle (degrees)")
        ax[2].grid()

        for a in ax:
            a.set_xlim(0, 360)

        wave_placeholder.pyplot(fig2)

        plt.close(fig2)  # ✅ VERY IMPORTANT (prevents crash)

        time.sleep(0.05)
# ================= INFO =================
st.subheader("📘 Working")

st.write(f"""
- T1 & T2 conduct from α to π  
- T3 & T4 conduct from π+α to 2π  
- Output controlled by firing angle  

Current α = {alpha_deg}°
""")
