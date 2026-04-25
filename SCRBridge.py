import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import time

# ================= PAGE =================
st.set_page_config(page_title="SCR Full Converter", layout="wide")
st.title("⚡ Single-Phase Fully Controlled Bridge Converter")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Controls")

Vm = st.sidebar.number_input("Peak Voltage (V)", value=325.0)
f = st.sidebar.number_input("Frequency (Hz)", value=50.0)
alpha_deg = st.sidebar.slider("Firing Angle α (deg)", 0, 180, 60)
R = st.sidebar.number_input("Load Resistance (Ω)", value=50.0)

run = st.sidebar.button("▶️ Start Simulation")

# ================= PRE-CALC =================
alpha = np.deg2rad(alpha_deg)
theta_all = np.linspace(0, 2*np.pi, 400)
theta_deg_all = np.degrees(theta_all)

vin = Vm * np.sin(theta_all)
vout = np.zeros_like(vin)
iout = np.zeros_like(vin)

# ================= PLACEHOLDERS =================
circuit_placeholder = st.empty()
wave_placeholder = st.empty()

# ================= CIRCUIT FUNCTION =================
def draw_circuit(pair):
    with schemdraw.Drawing() as d:

        # AC Source
        d += elm.SourceSin().label("AC")

        d += elm.Line().right()

        # Colors
        c1 = "red" if pair == "T1T2" else "black"
        c2 = "blue" if pair == "T3T4" else "black"

        # Top branch
        d.push()
        d += elm.Diode().right().label("T1").color(c1)
        d += elm.Line().right()
        d += elm.Resistor().down().label("Load")
        d += elm.Line().left()
        d += elm.Diode().left().label("T2").color(c1)
        d.pop()

        # Bottom branch
        d.push()
        d += elm.Diode().down().label("T3").color(c2)
        d += elm.Line().down()
        d += elm.Diode().up().label("T4").color(c2)
        d.pop()

        fig = d.draw()
        return fig.fig   # IMPORTANT

# ================= SIMULATION =================
if run:

    for i in range(len(theta_all)):

        theta = theta_all[i]

        # ===== SCR CONDUCTION =====
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

        # Current
        iout[i] = vout[i] / R

        # ===== DRAW CIRCUIT =====
        fig1 = draw_circuit(pair)
        circuit_placeholder.pyplot(fig1)

        # ===== WAVEFORMS =====
        fig2, ax = plt.subplots(3, 1, figsize=(10, 7))

        # Input Voltage
        ax[0].plot(theta_deg_all[:i+1], vin[:i+1])
        ax[0].axvline(alpha_deg, linestyle='--', color='red')
        ax[0].axvline(180 + alpha_deg, linestyle='--', color='blue')
        ax[0].set_title("Input Voltage with Firing Angles")
        ax[0].set_ylabel("Voltage (V)")
        ax[0].grid()

        # Output Voltage
        ax[1].plot(theta_deg_all[:i+1], vout[:i+1], color=color)
        ax[1].set_title("Output Voltage")
        ax[1].set_ylabel("Voltage (V)")
        ax[1].grid()

        # Output Current
        ax[2].plot(theta_deg_all[:i+1], iout[:i+1], color=color)
        ax[2].set_title("Load Current")
        ax[2].set_xlabel("Angle (degrees)")
        ax[2].set_ylabel("Current (A)")
        ax[2].grid()

        # Axis formatting
        for a in ax:
            a.set_xlim(0, 360)
            a.set_xticks([0, 90, 180, 270, 360])

        wave_placeholder.pyplot(fig2)

        plt.close(fig2)  # prevent memory crash

        time.sleep(0.05)

# ================= THEORY =================
st.subheader("📘 Working Principle")

st.write(f"""
- T1 & T2 conduct from α to π  
- T3 & T4 conduct from π + α to 2π  
- Output voltage controlled by firing angle  

### Current α = {alpha_deg}°
""")
