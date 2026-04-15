import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import tempfile

# --- Page Config ---
st.set_page_config(page_title="Half Wave Rectifier Pro", layout="wide")

st.title("⚡ Half Wave Rectifier with Animation & Ripple")

# ------------------ CIRCUIT ------------------
import tempfile
import schemdraw
import schemdraw.elements as elm

def draw_circuit(R, Vm, diode_on, use_filter=False, C_uF=0):
    d = schemdraw.Drawing()
    d.config(unit=3)

    #color = "green" if diode_on else "red"

    # --- Source ---
    V1 = d.add(elm.SourceSin().label(f'{Vm}V'))

    # --- Diode ---
    d.add(elm.Diode().right().color(color))

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
        d.add(elm.Line().right(1.5))   # shift right
        d.add(elm.Line().down())
        d.add(elm.Capacitor().label(f'C\n{C_uF}µF'))
        d.add(elm.Line().left().length(4.5))  # connect to return path
        d.add(elm.Line().up())
        d.pop()

    # Save image
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    d.save(tmp.name)

    return tmp.name

# ------------------ SIDEBAR ------------------
with st.sidebar:
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
        st.image(draw_circuit(
    R, Vm,
    diode_on_array[mid_index],
    use_filter,
    C_uF
))

        if diode_on_array[mid_index]:
            st.success("Diode ON")
        else:
            st.error("Diode OFF")

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
    st.subheader("Performance")

    col1, col2, col3 = st.columns(3)
    col1.metric("DC Voltage", f"{Vdc:.2f} V")
    col2.metric("Ripple Voltage", f"{Vr:.2f} V")
    col3.metric("Ripple Factor", f"{ripple_factor:.3f}")

    if use_filter:
        st.success("Filter reduces ripple ✔")
    else:
        st.warning("No filter → high ripple ⚠")
