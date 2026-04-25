import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="SCR Full Converter Pro", layout="wide")
st.title("⚡ Single-Phase Fully Controlled Bridge Converter")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Simulation Parameters")
Vm = st.sidebar.number_input("Peak Voltage (V)", value=325.0)
f = st.sidebar.number_input("Frequency (Hz)", value=50.0)
alpha_deg = st.sidebar.slider("Firing Angle α (deg)", 0, 180, 60)
R = st.sidebar.number_input("Load Resistance (Ω)", value=50.0)
load_type = st.sidebar.radio("Load Type", ["Resistive (R)", "Inductive (R-L)"])

# ================= CALCULATIONS =================
alpha = np.deg2rad(alpha_deg)
theta = np.linspace(0, 2*np.pi, 1000)
vin = Vm * np.sin(theta)

if load_type == "Resistive (R)":
    mask = ((theta >= alpha) & (theta <= np.pi)) | ((theta >= np.pi + alpha) & (theta <= 2*np.pi))
    vout = np.where(mask, np.abs(vin), 0)
    Vdc = (2 * Vm / np.pi) * np.cos(alpha)
else:
    vout = np.where((theta >= alpha) & (theta < np.pi + alpha), vin, -vin)
    Vdc = (2 * Vm / np.pi) * np.cos(alpha)

iout = vout / R

# ================= CIRCUIT DIAGRAM =================
st.subheader("🔌 Circuit Diagram")

# Determine active pair
pair = "T1T2" if alpha_deg < 90 else "T3T4"

def draw_circuit(pair):
    # Using the context manager ensures the figure is correctly initialized
    with schemdraw.Drawing(backend='matplotlib') as d:
        d.config(fontsize=12)
        
        # Define colors
        c1 = "red" if pair == "T1T2" else "black"
        c2 = "blue" if pair == "T3T4" else "black"
        
        # Circuit Layout
        d += elm.SourceSin().label("AC")
        d += elm.Line().right(1)
        d.push()
        d += elm.Line().up(1)
        # Left Leg
        d += (T1 := elm.SCR().label("T1").color(c1))
        # Load
        d += elm.Line().right()
        d += elm.Line().down()
        d += (L1 := elm.Resistor().down().label("Load"))
        d += elm.Line().down()
        d += elm.Line().left()
        d += (T2 := elm.Diode().label("T2").color(c1))
        d += elm.Line().left()
        d += elm.Line().up()
        d.pop()
        d += elm.Line().down(1)
        d += (T4 := elm.SCR().label("T4").color(c2).reverse())
        
        d += elm.Line().up()
        d += elm.Line().right()
        

        # Lower bridge
        d += elm.Line().left()
        
        
        # Return to source node for bottom diodes
        d.push()
        d += elm.Line().down()
        d += (T3 := elm.Diode().label("T3").color(c2))
        
        d.pop()
        
        return d.fig

# Render using the figure object directly
fig = draw_circuit(pair)
st.pyplot(fig)

# ================= WAVEFORMS =================
st.subheader("📈 Waveforms")
fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax[0].plot(np.degrees(theta), vin, label="Input Voltage", color="gray", linestyle="--")
ax[0].plot(np.degrees(theta), vout, label="Output Voltage", color="red", linewidth=2)
ax[0].set_title("Input vs Output Voltage")
ax[0].set_ylabel("Voltage (V)")
ax[0].grid(True); ax[0].legend()

# ================= MARKING ALPHA =================
# Add annotation for T1/T2 firing
ax[0].annotate(r'$\alpha$', xy=(alpha_deg, 0), xytext=(alpha_deg + 10, Vm/2),
               arrowprops=dict(facecolor='red', shrink=0.05), fontsize=12, color='red')

# Add annotation for T3/T4 firing (at 180 + alpha)
ax[0].annotate(r'$\pi+\alpha$', xy=(180 + alpha_deg, 0), xytext=(180 + alpha_deg + 10, Vm/2),
               arrowprops=dict(facecolor='blue', shrink=0.05), fontsize=12, color='blue')

ax[1].plot(np.degrees(theta), iout, label="Load Current", color="blue", linewidth=2)
ax[1].set_title("Load Current")
ax[1].set_xlabel("Angle (degrees)")
ax[1].set_ylabel("Current (A)")
ax[1].grid(True); ax[1].legend()

st.pyplot(fig)

# ================= RESULTS & THEORY =================
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Output Metrics")
    st.metric("Avg Output Voltage (Vdc)", f"{Vdc:.2f} V")
    st.metric("Avg Load Current (Idc)", f"{Vdc/R:.2f} A")

with col2:
    st.subheader("📘 Theoretical Background")
    st.latex(r"V_{dc} = \frac{2V_m}{\pi} \cos(\alpha)")
    st.write("SCRs fire in diagonal pairs to rectify the AC waveform.")
