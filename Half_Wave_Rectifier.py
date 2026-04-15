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
def draw_circuit(R, Vm, diode_on):
    d = schemdraw.Drawing()
    d.config(unit=3)

    color = "green" if diode_on else "red"

    V1 = d.add(elm.SourceSin().label(f'{Vm}V'))

    d.add(elm.Diode().right().color(color).label("ON" if diode_on else "OFF"))

    d.add(elm.Resistor().down().label(f'R\n{R}Ω'))

    d.add(elm.Line().left().to(V1.start))
    d.add(elm.Line().up())

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
tab1, tab2, tab3 = st.tabs(["🔌 Circuit", "📈 Waveform", "📊 Results"])

# ------------------ CIRCUIT ------------------
with tab1:
    st.subheader("Animated Diode State")

    # pick mid-point state for display
    mid_index = len(diode_on_array)//2
    st.image(draw_circuit(R, Vm, diode_on_array[mid_index]))

    if diode_on_array[mid_index]:
        st.success("Diode is ON (Conducting)")
    else:
        st.error("Diode is OFF (Blocking)")

# ------------------ WAVEFORM ------------------
with tab2:
    st.subheader("Waveform with Ripple")

    fig, ax = plt.subplots()

    ax.plot(t, vin, linestyle='dashed', label="Input AC")
    ax.plot(t, vout, label="Rectified")
    ax.plot(t, vout_final, linewidth=2, label="Filtered Output")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.grid()
    ax.legend()

    st.pyplot(fig)

# ------------------ RESULTS ------------------
with tab3:
    st.subheader("Performance")

    col1, col2, col3 = st.columns(3)
    col1.metric("DC Voltage", f"{Vdc:.2f} V")
    col2.metric("Ripple Voltage", f"{Vr:.2f} V")
    col3.metric("Ripple Factor", f"{ripple_factor:.3f}")

    if use_filter:
        st.success("Filter reduces ripple ✔")
    else:
        st.warning("No filter → high ripple ⚠")
