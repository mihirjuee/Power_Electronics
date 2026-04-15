import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import tempfile

# --- Page Config ---
st.set_page_config(
    page_title="Half Wave Rectifier",
    page_icon="logo.png",
    layout="wide"
)

st.title("⚡ Half Wave Rectifier ")

# ------------------ CIRCUIT ------------------
import tempfile
import schemdraw
import schemdraw.elements as elm

def draw_circuit(R, Vm, use_filter=False, C_uF=0):
    d = schemdraw.Drawing()
    d.config(unit=3)

    #color = "green" if diode_on else "red"

    # --- Source ---
    V1 = d.add(elm.SourceSin().label(f'{Vm}V'))

    # --- Diode ---
    d.add(elm.Diode().right())

    # --- Top node ---
    d.add(elm.Dot())

    # ----------- MAIN PATH (Resistor branch) -----------
    d.push()
    d.add(elm.Line().down())
    d.add(elm.Resistor().label(f'R\n{R}Ω'))
    d.add(elm.Line().left().length(3))
    d.add(elm.Line().up().to(V1.start))
    d.pop()

    # ----------- CAPACITOR BRANCH (SHIFTED RIGHT) -----------
    if use_filter:
        d.push()
        d.add(elm.Line().right(2.5))   # shift right
        d.add(elm.Line().down())
        d.add(elm.Capacitor().label(f'C\n{C_uF}µF'))
        d.add(elm.Line().left().length(5.5))  # connect to return path
        d.add(elm.Line().up())
        d.pop()

    # Save image
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    d.save(tmp.name)

    return tmp.name

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    
    st.markdown("---")
    st.header("Controls")

    Vm = st.slider("Peak Voltage (Vm)", 1, 325, 100)
    freq = st.slider("Frequency (Hz)", 1, 100, 50)
    R = st.slider("Load Resistance (Ω)", 1, 1000, 100)

    st.markdown("### Filter")
    use_filter = st.toggle("Add Capacitor Filter")
    C_uF = st.slider("Capacitance (µF)", 1, 1000, 100) if use_filter else 0

# ------------------ TIME ------------------
t = np.linspace(0, 2*(1/freq), 2000)

vin = Vm * np.sin(2 * np.pi * freq * t)

# ------------------ DIODE LOGIC ------------------
diode_on_array = vin > 0
vout = np.maximum(0, vin)

# ------------------ CAPACITOR FILTER ------------------
if use_filter:
    C = C_uF * 1e-6
    v_filtered = np.zeros_like(vout)

    for i in range(1, len(vout)):
        if vout[i] > v_filtered[i-1]:
            v_filtered[i] = vout[i]  # charging
        else:
            # discharging
            v_filtered[i] = v_filtered[i-1] * np.exp(-1/(R*C*freq*100))

    vout_final = v_filtered
else:
    vout_final = vout

# ------------------ RIPPLE ------------------
Vdc = np.mean(vout_final)
Vr = np.max(vout_final) - np.min(vout_final)
ripple_factor = Vr / Vdc if Vdc != 0 else 0


# ------------------ TABS ------------------
tab1, tab2 = st.tabs(["🔌 Simulation", "📊 Results"])

# ------------------ SIMULATION TAB ------------------
with tab1:
    st.subheader("Circuit & Waveform")

    col1, col2 = st.columns(2)

    # --- Circuit ---
with col1:
        st.markdown("### Circuit")
        mid_index = len(diode_on_array)//2
        st.image(draw_circuit(R, Vm, use_filter, C_uF))


    # --- Waveform ---
with col2:
        st.markdown("### Waveform")

        fig, ax = plt.subplots()

        ax.plot(t, vin, linestyle='dashed', label="Input AC")
        ax.plot(t, vout, label="Rectified")
        ax.plot(t, vout_final, linewidth=2, label="Filtered")

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Voltage (V)")
        ax.grid()
        ax.legend()

        st.pyplot(fig)

# ------------------ RESULTS TAB ------------------
with tab2:
    st.subheader("📘 Key Formulas")

    st.latex(r"DC \hspace{0.2cm} Output \hspace{0.2cm} Voltage,\hspace{0.2cm} V_{DC} = \frac{V_m}{\pi}")
    st.latex(r"RMS \hspace{0.2cm} Output \hspace{0.2cm} Voltage,\hspace{0.2cm} V_{RMS} = \frac{V_m}{2}")
    st.latex(r" Ripple \hspace{0.2cm} factor \hspace{0.2cm}(without \hspace{0.2cm} capcitor), r = \sqrt{\left(\frac{V_{RMS}}{V_{DC}}\right)^2 - 1}")
    st.latex(r"Ripple \hspace{0.2cm} factor \hspace{0.2cm}(with \hspace{0.2cm} capcitor), r \approx \frac{1}{2\sqrt{3} f R C}")

    st.subheader("📊 Calculated Results")

    Vdc = Vm / np.pi
    Vrms = Vm / 2

    st.write(f"DC Output Voltage: {Vdc:.2f} V")
    st.write(f"Output RMS  Voltage: {Vrms:.2f} V")

    # ✅ Ripple WITHOUT capacitor
    r_no_filter = np.sqrt((Vrms / Vdc)**2 - 1)
    st.write(f"Ripple Factor (Without Filter): {r_no_filter:.4f}")

    # ✅ Ripple WITH capacitor
    if use_filter:
        C = C_uF * 1e-6
        r_with_filter = 1 / (2 * np.sqrt(3) * freq * R * C)
        st.write(f"Ripple Factor (With Capacitor): {r_with_filter:.4f}")

        st.success("Capacitor reduces ripple significantly ✔")
    else:
        st.info("Enable capacitor filter to see reduced ripple")
