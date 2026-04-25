import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="SCR Full Converter", layout="wide")
st.title("⚡ Single-Phase Fully Controlled Bridge Converter")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Controls")

Vm = st.sidebar.number_input("Peak Voltage (V)", value=325.0)
f = st.sidebar.number_input("Frequency (Hz)", value=50.0)
alpha_deg = st.sidebar.slider("Firing Angle α (deg)", 0, 180, 60)
R = st.sidebar.number_input("Load Resistance (Ω)", value=50.0)

# ================= CALCULATIONS =================
alpha = np.deg2rad(alpha_deg)

theta = np.linspace(0, 2*np.pi, 1000)
theta_deg = np.degrees(theta)

vin = Vm * np.sin(theta)
vout = np.zeros_like(vin)

# Output waveform
for i in range(len(theta)):
    if alpha <= theta[i] <= np.pi:
        vout[i] = Vm * np.sin(theta[i])
    elif np.pi + alpha <= theta[i] <= 2*np.pi:
        vout[i] = Vm * np.sin(theta[i])
    else:
        vout[i] = 0

iout = vout / R

# ================= DETERMINE ACTIVE SCR =================
# just for diagram (based on α position)
if alpha < np.pi:
    pair = "T1T2"
else:
    pair = "T3T4"

# ================= CIRCUIT =================
st.subheader("🔌 Circuit Diagram")

def draw_circuit(pair):
    with schemdraw.Drawing() as d:

        d += elm.SourceSin().label("AC")
        d += elm.Line().right()

        c1 = "red" if pair == "T1T2" else "black"
        c2 = "blue" if pair == "T3T4" else "black"

        # Top
        d.push()
        d += elm.Diode().right().label("T1").color(c1)
        d += elm.Line().right()
        d += elm.Resistor().down().label("Load")
        d += elm.Line().left()
        d += elm.Diode().left().label("T2").color(c1)
        d.pop()

        # Bottom
        d.push()
        d += elm.Diode().down().label("T3").color(c2)
        d += elm.Line().down()
        d += elm.Diode().up().label("T4").color(c2)
        d.pop()

        fig = d.draw()
        return fig.fig

st.pyplot(draw_circuit(pair))

# ================= WAVEFORMS =================
st.subheader("📈 Waveforms")

fig, ax = plt.subplots(3, 1, figsize=(10, 7))

# Input
ax[0].plot(theta_deg, vin)
ax[0].axvline(alpha_deg, linestyle='--', color='red')
ax[0].axvline(180 + alpha_deg, linestyle='--', color='blue')
ax[0].set_title("Input Voltage with Firing Angle")
ax[0].set_ylabel("Voltage (V)")
ax[0].grid()

# Output Voltage
ax[1].plot(theta_deg, vout, color='green')
ax[1].set_title("Output Voltage")
ax[1].set_ylabel("Voltage (V)")
ax[1].grid()

# Output Current
ax[2].plot(theta_deg, iout, color='purple')
ax[2].set_title("Load Current")
ax[2].set_xlabel("Angle (degrees)")
ax[2].set_ylabel("Current (A)")
ax[2].grid()

# Axis formatting
for a in ax:
    a.set_xlim(0, 360)
    a.set_xticks([0, 90, 180, 270, 360])

st.pyplot(fig)

# ================= RESULTS =================
Vdc = (2 * Vm / np.pi) * np.cos(alpha)
Idc = Vdc / R

st.subheader("📊 Output Values")

c1, c2 = st.columns(2)
c1.metric("Average Output Voltage", f"{Vdc:.2f} V")
c2.metric("Average Load Current", f"{Idc:.2f} A")

# ================= THEORY =================
st.subheader("📘 Working")

st.write(f"""
- T1 & T2 conduct from α to π  
- T3 & T4 conduct from π + α to 2π  
- Output controlled by firing angle  

### Current α = {alpha_deg}°
""")
