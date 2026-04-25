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
    for i in range(len(t)):

        theta = t[i]

        # Determine conducting SCR pair
        if alpha <= theta <= np.pi:
            pair = "T1T2"
        elif np.pi + alpha <= theta <= 2*np.pi:
            pair = "T3T4"
        else:
            pair = "NONE"

        # Draw circuit
        fig1 = draw_circuit(pair)
        circuit_placeholder.pyplot(fig1)

        # Firing pulse visualization
        pulse = np.zeros_like(t[:i+1])

        for k in range(i+1):
            th = t[k]
            if abs(th - alpha) < 0.05 or abs(th - (np.pi + alpha)) < 0.05:
                pulse[k] = 1

        fig2, ax = plt.subplots(figsize=(8,3))
        ax.plot(t[:i+1], pulse)
        ax.set_title("Firing Pulses")
        ax.set_ylim(-0.2, 1.2)
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
