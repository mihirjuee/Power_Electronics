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
import io
from PIL import Image

st.subheader("🔌 Circuit Diagram (6-Diode Bridge)")

d = schemdraw.Drawing()

# Example simple diagram (you can keep your existing one)
d += elm.SourceSin().label("3-Phase AC")
d += elm.Line().right(2)
d += elm.Diode().down().label("D1")
d += elm.Line().down()
d += elm.Diode().left().label("D2")
d += elm.Line().up()
d += elm.Line().right().label("+Vdc")
d += elm.Dot()
d += elm.Line().down(2)
d += elm.Dot().label("-Vdc")

# ---- KEY FIX ----
buf = io.BytesIO()
d.save(buf)          # Save drawing to buffer
buf.seek(0)

img = Image.open(buf)

# Convert to matplotlib figure
fig, ax = plt.subplots()
ax.imshow(img)
ax.axis('off')

st.pyplot(fig)

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
