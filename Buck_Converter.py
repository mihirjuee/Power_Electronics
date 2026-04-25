import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import time

# ================= PAGE =================
st.set_page_config(page_title="PWM Buck Converter", layout="wide")
st.title("⚡ Buck Converter with PWM & MOSFET")

st.latex(r"V_o = D \cdot V_{in}")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Controls")

Vin = st.sidebar.number_input("Input Voltage (V)", 12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 1.0, 0.5)
fs = st.sidebar.number_input("Switching Frequency (Hz)", 20000.0)

R = st.sidebar.number_input("Load Resistance (Ω)", 10.0)
L = st.sidebar.number_input("Inductance (H)", 1e-3, format="%.5f")
C = st.sidebar.number_input("Capacitance (F)", 100e-6, format="%.6f")

run = st.sidebar.button("▶️ Start PWM Animation")

# ================= TIME =================
T = 1 / fs
t = np.linspace(0, 5*T, 1000)

# PWM signal
pwm = (t % T) < (D * T)

# ================= PLACEHOLDERS =================
diagram_placeholder = st.empty()
wave_placeholder = st.empty()

# ================= FUNCTION: DRAW CIRCUIT =================
def draw_circuit(state):
    with schemdraw.Drawing() as d:

        # Input source
        d += elm.SourceV().label('Vin')
        d += elm.Line().right()

        # MOSFET
        mos_label = "ON" if state else "OFF"
        mos = elm.NFet().label(f"MOSFET\n({mos_label})")
        d += mos

        # Node after MOSFET
        d += elm.Line().right()

        # Save node for diode branch
        d.push()

        # Inductor path
        d += elm.Inductor().label('L')
        d += elm.Line().right()
        d += elm.Dot()

        # Output capacitor
        d.push()
        d += elm.Capacitor().down().label('C')
        d += elm.Ground()
        d.pop()

        # Load resistor
        d += elm.Line().right()
        d += elm.Resistor().down().label('R')
        d += elm.Ground()

        # Back to switch node
        d.pop()

        # Freewheeling diode branch (CORRECT WAY)
        d += elm.Diode().down().label('D')
        d += elm.Ground()

        return d.draw()

# ================= ANIMATION =================
if run:
    for i in range(50):  # frames
        idx = int(i * len(t) / 50)
        state = pwm[idx]

        # Update circuit
        fig1 = draw_circuit(state)
        diagram_placeholder.pyplot(fig1)

        # Plot PWM waveform
        fig2, ax = plt.subplots(figsize=(8, 3))
        ax.plot(t[:idx]*1e6, pwm[:idx])
        ax.set_title("PWM Gate Signal")
        ax.set_xlabel("Time (µs)")
        ax.set_ylim(-0.2, 1.2)
        ax.grid()

        wave_placeholder.pyplot(fig2)

        time.sleep(0.1)

# ================= RESULTS =================
Vo = D * Vin
Io = Vo / R

st.subheader("📊 Output")
c1, c2 = st.columns(2)
c1.metric("Output Voltage", f"{Vo:.2f} V")
c2.metric("Output Current", f"{Io:.2f} A")
