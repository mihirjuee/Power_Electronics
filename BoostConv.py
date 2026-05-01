import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Boost Converter Pro", page_icon="⚡", layout="wide")
st.title("⚡ Boost Converter Analysis Tool")

# ================= SIDEBAR =================
st.sidebar.header("🔧 System Parameters")

Vin = st.sidebar.number_input("Input Voltage (V)", value=12.0)
D = st.sidebar.slider("Duty Cycle", 0.0, 0.95, 0.5)
fs = st.sidebar.number_input("Switching Frequency (Hz)", value=50000.0)

R = st.sidebar.number_input("Load Resistance (Ω)", value=50.0)
L = st.sidebar.number_input("Inductance (H)", value=200e-6, format="%.6f")
C = st.sidebar.number_input("Capacitance (F)", value=220e-6, format="%.6f")

# ================= CALCULATION =================
T = 1 / fs
t = np.linspace(0, 10*T, 6000)
dt = t[1] - t[0]

IL = np.zeros_like(t)
Vo = np.zeros_like(t)
VL = np.zeros_like(t)

# Initial condition
Vo[0] = Vin / max((1 - D), 0.05)

for i in range(1, len(t)):

    switch_on = 1 if (t[i] % T) < (D * T) else 0

    # ---------------- SWITCH ON ----------------
    if switch_on:
        # Inductor charges from source
        VL[i] = Vin
        IL[i] = IL[i-1] + (VL[i] / L) * dt

        # Capacitor supplies load
        IC = -Vo[i-1] / R

    # ---------------- SWITCH OFF ----------------
    else:
        # Inductor discharges to load + source
        VL[i] = Vin - Vo[i-1]
        IL[i] = IL[i-1] + (VL[i] / L) * dt

        if IL[i] < 0:
            IL[i] = 0

        IC = IL[i] - (Vo[i-1] / R)

    # Capacitor voltage update
    Vo[i] = Vo[i-1] + (IC / C) * dt

# ================= STEADY STATE =================
steady = int(0.6 * len(t))

Vo_ss = Vo[steady:]
IL_ss = IL[steady:]
VL_ss = VL[steady:]

Vo_avg = np.mean(Vo_ss)
Vripple = np.max(Vo_ss) - np.min(Vo_ss)
ripple_pct = (Vripple / Vo_avg) * 100 if Vo_avg != 0 else 0

IL_peak = np.max(IL_ss)
IL_avg = np.mean(IL_ss)

Pin = Vin * IL_avg
Pout = (Vo_avg ** 2) / R
eff = (Pout / Pin) * 100 if Pin > 0 else 0

mode = "DCM" if np.min(IL_ss) <= 1e-4 else "CCM"

# Theoretical boost voltage
Vo_theory = Vin / (1 - D) if D < 1 else np.inf

# ================= CIRCUIT =================
st.subheader("🔌 Circuit Diagram")

with schemdraw.Drawing() as d:
    d += elm.SourceV().label(f'{Vin} V')
    d += elm.Line().right(1)

    # Inductor
    d += elm.Inductor().right().label("L")

    # Switch node
    d += elm.Dot()

    # MOSFET branch
    d.push()
    d += elm.Line().down(1.5)
    d += elm.NFet().label("MOSFET")
    d += elm.Line().down(1)
    d += elm.Ground()
    d.pop()

    # Diode to output
    d += elm.Diode().right().label("D")
    d += elm.Dot()

    # Capacitor branch
    d.push()
    d += elm.Capacitor().down().label("C")
    d += elm.Ground()
    d.pop()

    # Load
    d += elm.Line().right(1.5)
    d += elm.Resistor().down().label("R")
    d += elm.Ground()

    fig_circuit = d.draw().fig

st.pyplot(fig_circuit)

# ================= MODE =================
st.metric("Operating Mode", mode)

# ================= WAVEFORMS =================
st.subheader("📈 Steady-State Waveforms")

fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)

# Output Voltage
axes[0].plot(t[steady:] * 1e6, Vo_ss, color='red', linewidth=2, label="Vo")
axes[0].axhline(Vo_avg, linestyle='--', linewidth=1.5,
                label=f"Avg = {Vo_avg:.2f} V")

axes[0].fill_between(
    t[steady:] * 1e6,
    Vo_avg - Vripple/2,
    Vo_avg + Vripple/2,
    alpha=0.2,
    label="Ripple Band"
)

axes[0].set_ylabel("Vo (V)")
axes[0].set_title("Output Voltage")
axes[0].legend()
axes[0].grid(True)

# Inductor Current
axes[1].plot(t[steady:] * 1e6, IL_ss, color='blue', linewidth=2)
axes[1].set_ylabel("iL (A)")
axes[1].set_title("Inductor Current")
axes[1].grid(True)

# Inductor Voltage
axes[2].plot(t[steady:] * 1e6, VL_ss, color='green', linewidth=2)
axes[2].set_ylabel("VL (V)")
axes[2].set_xlabel("Time (µs)")
axes[2].set_title("Inductor Voltage")
axes[2].grid(True)

plt.tight_layout(h_pad=3)
st.pyplot(fig)

# ================= RIPPLE ZOOM =================
st.subheader("🔍 Output Voltage Ripple (Zoomed)")

fig2, ax2 = plt.subplots(figsize=(9, 3))
ax2.plot(t[steady:] * 1e6, Vo_ss, linewidth=2)
ax2.set_ylim(Vo_avg - 2*Vripple, Vo_avg + 2*Vripple)
ax2.set_xlabel("Time (µs)")
ax2.set_ylabel("Voltage (V)")
ax2.set_title("Ripple Zoom")
ax2.grid(True)

st.pyplot(fig2)

# ================= METRICS =================
st.subheader("📊 Key Performance Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Vo Avg", f"{Vo_avg:.2f} V")
c2.metric("Theoretical Vo", f"{Vo_theory:.2f} V")
c3.metric("Ripple (ΔVo)", f"{Vripple:.4f} V")
c4.metric("Ripple %", f"{ripple_pct:.2f} %")

c5, c6, c7 = st.columns(3)

c5.metric("Efficiency", f"{eff:.2f} %")
c6.metric("Inductor Peak Current", f"{IL_peak:.2f} A")
c7.metric("Average Inductor Current", f"{IL_avg:.2f} A")

# ================= THEORY =================
with st.expander("📘 Boost Converter Theory"):
    st.markdown("""
    ### Ideal Boost Converter:
    **Output Voltage:**
    Vo = Vin / (1 - D)

    ### ON State:
    - Switch ON
    - Inductor stores energy
    - Diode OFF
    - Capacitor supplies load

    ### OFF State:
    - Switch OFF
    - Inductor releases energy
    - Diode ON
    - Output voltage boosted above input

    ### Modes:
    ✅ CCM: Inductor current never reaches zero  
    ✅ DCM: Inductor current becomes zero

    ### Ripple:
    Ripple % = (ΔVo / Vo_avg) × 100
    """)
# ================= KEY FORMULAS SECTION =================
# ADD THIS near the bottom of your Boost Converter app
# (Place before st.info or footer)

st.subheader("📐 Key Boost Converter Formulas")

colf1, colf2 = st.columns(2)

with colf1:
    st.latex(r"V_o = \frac{V_{in}}{1-D}")
    st.caption("Ideal Output Voltage")

    st.latex(r"I_o = \frac{V_o}{R}")
    st.caption("Load Current")

    st.latex(r"I_{in} = \frac{I_o}{1-D}")
    st.caption("Input / Inductor Average Current (Ideal)")

    st.latex(r"T = \frac{1}{f_s}")
    st.caption("Switching Time Period")

with colf2:
    st.latex(r"\Delta I_L = \frac{V_{in}D}{Lf_s}")
    st.caption("Inductor Current Ripple")

    st.latex(r"\Delta V_o = \frac{I_o D}{C f_s}")
    st.caption("Output Voltage Ripple Approximation")

    st.latex(r"\%Ripple = \frac{\Delta V_o}{V_o}\times100")
    st.caption("Ripple Percentage")

    st.latex(r"\eta = \frac{P_{out}}{P_{in}}\times100")
    st.caption("Efficiency")

# ================= CCM / DCM BOUNDARY =================
st.subheader("⚙️ CCM / DCM Boundary")

R_critical = (2 * L * fs) / ((1 - D) ** 2) if D < 1 else np.inf

colm1, colm2, colm3 = st.columns(3)

colm1.metric("Critical Resistance", f"{R_critical:.2f} Ω")
colm2.metric("Current Mode", mode)
colm3.metric(
    "Condition",
    "CCM" if R < R_critical else "DCM"
)

# ================= DESIGN INSIGHT =================
with st.expander("🧠 Formula Insights"):
    st.markdown("""
    ### Important Design Relationships:

    **Higher Duty Cycle (D ↑):**
    - Output voltage increases sharply
    - Inductor current stress increases
    - Ripple may increase
    - Practical losses rise

    **Higher Inductance (L ↑):**
    - Lower current ripple
    - Better CCM stability
    - Slower transient response

    **Higher Capacitance (C ↑):**
    - Lower output voltage ripple
    - Better filtering
    - Larger physical size

    **Higher Switching Frequency (fs ↑):**
    - Smaller L and C possible
    - Lower ripple
    - Higher switching losses in real systems
    """)
# ================= INFO =================
st.info("Ideal boost model (no switching/conduction losses). Increase duty cycle carefully as D → 1 causes very high theoretical voltage.")
