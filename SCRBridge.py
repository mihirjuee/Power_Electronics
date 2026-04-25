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

    for i in range(len(theta_all)):

        theta = theta_all[i]
        theta_deg = theta_deg_all[i]

        # ================= SCR CONDUCTION =================
        if alpha <= theta <= np.pi:
            pair = "T1T2"
        elif np.pi + alpha <= theta <= 2*np.pi:
            pair = "T3T4"
        else:
            pair = "NONE"

        # ================= CIRCUIT =================
        fig1 = draw_circuit(pair)
        circuit_placeholder.pyplot(fig1)

        # ================= FIRING PULSES =================
        pulse = np.zeros(i+1)

        for k in range(i+1):
            th = theta_all[k]

            # Narrow pulse width (~2 degrees)
            if (alpha <= th <= alpha + np.deg2rad(2)) or \
               (np.pi + alpha <= th <= np.pi + alpha + np.deg2rad(2)):
                pulse[k] = 1

        # ================= PLOT =================
        fig2, ax = plt.subplots(figsize=(8,3))

        ax.plot(theta_deg_all[:i+1], pulse)

        ax.set_title("Firing Pulses vs Angle")
        ax.set_xlabel("Angle (degrees)")
        ax.set_ylabel("Pulse")

        ax.set_xlim(0, 360)
        ax.set_ylim(-0.2, 1.2)

        # Mark firing angles
        ax.axvline(alpha_deg, linestyle='--')
        ax.axvline(180 + alpha_deg, linestyle='--')

        # Better ticks
        ax.set_xticks([0, 90, 180, 270, 360])

        ax.grid()

        wave_placeholder.pyplot(fig2)

        time.sleep(0.05)

# ================= INFO =================
st.subheader("📘 Working")

st.write(f"""
- T1 & T2 conduct from α to π  
- T3 & T4 conduct from π+α to 2π  
- Output controlled by firing angle  

Current α = {alpha_deg}°
""")
