import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="3-Phase Rectifier", layout="wide")

st.title("⚡ 3-Phase Uncontrolled Rectifier (6-Pulse)")

st.latex(r"V_{dc} = 1.35 \, V_{LL}")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Input Parameters")

V_ll = st.sidebar.slider("Line Voltage V_LL (RMS)", 100, 500, 400)
f = st.sidebar.slider("Frequency (Hz)", 25, 60, 50)

# ================= CALCULATIONS =================
Vm = np.sqrt(2) * (V_ll / np.sqrt(3))

t = np.linspace(0, 2*np.pi, 1000)

Va = Vm * np.sin(t)
Vb = Vm * np.sin(t - 2*np.pi/3)
Vc = Vm * np.sin(t - 4*np.pi/3)

Vab = Va - Vb
Vbc = Vb - Vc
Vca = Vc - Va

Vdc = np.maximum.reduce([Vab, Vbc, Vca])
Vdc_avg = np.mean(Vdc)

# ================= METRICS =================
col1, col2 = st.columns(2)
col1.metric("Average DC Output Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Expected (1.35 × V_LL)", f"{1.35 * V_ll:.2f} V")

# ================= CIRCUIT DIAGRAM =================
st.subheader("🔌 Circuit Diagram (6-Diode Bridge)")

d = schemdraw.Drawing()

# AC input lines
d += elm.Line().right().label("R", loc="left")
d.push()
d += elm.Line().down(2)

d.pop()
d += elm.Line().down().label("Y", loc="left")
d.push()
d += elm.Line().down(2)

d.pop()
d += elm.Line().down().label("B", loc="left")

# Top diodes (positive group)
d.push()
d += elm.Diode().right().label("D1")
d += elm.Line().right(2)
d += elm.Dot().label("+Vdc", loc="right")
d.pop()

d.push()
d += elm.Line().down()
d += elm.Diode().right().label("D3")
d += elm.Line().right(2)
d.pop()

d.push()
d += elm.Line().down(2)
d += elm.Diode().right().label("D5")
d += elm.Line().right(2)
d.pop()

# Bottom diodes (negative group)
d.push()
d += elm.Line().right(4)
d += elm.Line().down()
d += elm.Diode().left().label("D4")
d.pop()

d.push()
d += elm.Line().down(2)
d += elm.Line().right(4)
d += elm.Diode().left().label("D6")
d.pop()

d.push()
d += elm.Line().down(3)
d += elm.Line().right(4)
d += elm.Diode().left().label("D2")
d += elm.Dot().label("-Vdc", loc="right")
d.pop()

st.pyplot(d.draw())

# ================= PLOTS =================
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax[0].plot(t, Va, label="Va")
ax[0].plot(t, Vb, label="Vb")
ax[0].plot(t, Vc, label="Vc")
ax[0].set_title("Three Phase Voltages")
ax[0].legend()
ax[0].grid()

ax[1].plot(t, Vdc)
ax[1].set_title("Rectified Output Voltage (6-Pulse DC)")
ax[1].grid()

ax[1].set_xlabel("Electrical Angle (rad)")

st.pyplot(fig)

# ================= INFO =================
st.markdown("""
### 🔍 Working Insight:
- Top diodes (D1, D3, D5) connect the **most positive phase**
- Bottom diodes (D2, D4, D6) connect the **most negative phase**
- Conduction changes every **60°**

### ⚡ Result:
- 6 pulses per cycle
- Smooth DC output
""")
