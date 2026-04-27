import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="3-Phase Rectifier", page_icon="logo.png", layout="wide")

st.title("⚡ 3-Phase Uncontrolled Rectifier (6-Pulse)")

st.latex(r"V_{dc} = 1.35 \times V_{LL}")

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

# DC calculation based on line-to-line envelopes
Vdc = np.maximum.reduce([Va-Vb, Va-Vc, Vb-Va, Vb-Vc, Vc-Va, Vc-Vb])
Vdc_avg = np.mean(Vdc)

# ================= METRICS =================
col1, col2 = st.columns(2)
col1.metric("Average DC Output Voltage", f"{Vdc_avg:.2f} V")
col2.metric("Expected (1.35 × V_LL)", f"{1.35 * V_ll:.2f} V")

# ================= CIRCUIT DIAGRAM (FULL 6-DIODE BRIDGE) =================
st.subheader("🔌 3-Phase Rectifier Bridge")

import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing() as d:

    # ================= AC SOURCES =================
    d += elm.Line().at((0, 0)).right(1)
    S1 = d.add(elm.SourceSin().right().label("Van"))
    d += elm.Dot()
    d += elm.Line().at((0, 2)).right(1)
    S2 = d.add(elm.SourceSin().right().label("Vbn"))
    d += elm.Line().right(1)
    
    d += elm.Line().at((0, 4)).right(1)
    S3 = d.add(elm.SourceSin().right().label("Vcn"))
    d += elm.Line().right(2)
    

    # ================= TOP DIODES =================
    d += elm.Line().at(S1.end).up(4.5)
    D1 = d.add(elm.Diode().up(2).label("D1"))
    d += elm.Line().up(0.5)
    d.push()
    d += elm.Line().at(S2.end).right(2)
    d.push()
    d += elm.Dot()
    d += elm.Line().up(2)
    D3 = d.add(elm.Diode().up().label("D3"))
    #d += elm.Line().up(0.25)
    d += elm.Line().at(S3.end).right(3.5)
    d.push()
    d += elm.Dot()
    D5 = d.add(elm.Diode().up().label("D5"))
    d.pop()
    d += elm.Line().down(4)
    D2 = d.add(elm.Diode().down().reverse().label("D2"))
    #d += elm.Line().down(0.5)
    # ================= BOTTOM DIODES =================
    D4 = d.add(elm.Diode().at(S1.end).down().reverse().label("D4"))
    d.pop()
    d += elm.Line().down(2)
    D6 = d.add(elm.Diode().down().reverse().label("D6"))
    d += elm.Line().at(S3.end).right(1)
    

    # ================= DC BUS (TOP) =================
    d.pop()
    d += elm.Line().right(2)
    d += elm.Line().to(D5.end)

    # ================= LOAD =================
    d += elm.Line().right(2)
    d += elm.Line().down(3.5)
    R = d.add(elm.Resistor().down().label("Load"))
    d += elm.Line().down(3.5)
    d += elm.Line().left(2)
    # ================= DC BUS (BOTTOM) =================
    d += elm.Line().at(D4.end).to(D6.end)
    d += elm.Line().to(D2.end)
    #d += elm.Line().right().to(R.start)
    d += elm.Line().at((0, 0)).up(4)
    d += elm.Dot().at((0, 2)).label("n", loc="left")
# ===== DISPLAY FIX =====
import io
from PIL import Image
import matplotlib.pyplot as plt

buf = io.BytesIO()
d.save(buf)
buf.seek(0)

img = Image.open(buf)

fig, ax = plt.subplots()
ax.imshow(img)
ax.axis('off')

st.pyplot(fig)

# ================= PLOTS =================
# ================= CALCULATIONS (Updated for 6-Pulse Labels) =================
# We need an array to define the active diode conduction pairs
# Every 60 degrees (pi/3 radians), the conduction pair changes.
# The standard sequence for a 3-phase full bridge (with standard phase indexing) is:
# D6&D1, D1&D2, D2&D3, D3&D4, D4&D5, D5&D6.
# Let's adjust this for the visual matching image_0.png's style (6.1, 1.2, etc.)

intervals = np.arange(0, 2 * np.pi + np.pi/6, np.pi/3) # 60 degree intervals
labels = ['6,1', '1,2', '2,3', '3,4', '4,5', '5,6', '6,1']
line_labels = ['ab', 'ac', 'bc', 'ba', 'ca', 'cb', 'ab']

# Ensure calculations section includes all combinations for line-to-line:
Vab = Va - Vb
Vac = Va - Vc
Vbc = Vb - Vc
Vba = Vb - Va
Vca = Vc - Va
Vcb = Vc - Vb

# Re-calculate Vdc to follow these specific segments strictly for labelling
Vdc_segments = np.zeros_like(t)
# Conditions based on 60-degree intervals (starting at 30 degrees to match typical plots)
for i in range(len(intervals) - 1):
    # Adjust for initial 30-degree offset often used in textbook plots for symmetry
    t_start = intervals[i] + np.pi/6
    t_end = intervals[i+1] + np.pi/6
    mask = (t >= t_start) & (t < t_end)
    # The image shows "ab", "ac", etc. sequence
    line_voltages = [Vab, Vac, Vbc, Vba, Vca, Vcb, Vab]
    if i < len(line_voltages):
        Vdc_segments[mask] = line_voltages[i][mask]

# Clean up Vdc definition
Vdc_final = Vdc_segments

# ================= PLOTS =================
st.subheader("📊 Waveform Analysis (Detailed Conduction)")

# Layout similar to image_0.png: Source Plot (Top), Bridge Plot (Bottom)
fig, ax = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={'height_ratios': [1, 2]})

# --- TOP PLOT: Source (Phase-to-Neutral) ---
ax[0].plot(t, Va, 'r-', label='an', alpha=0.7)
ax[0].plot(t, Vb, 'g-', label='bn', alpha=0.7)
ax[0].plot(t, Vc, 'b-', label='cn', alpha=0.7)
ax[0].set_ylabel('Source Voltage (V)')
ax[0].set_title('Source Phase-to-Neutral Voltages')
ax[0].grid(True, which='both', linestyle='--', alpha=0.5)

# Label phases at peaks (matching 'an', 'bn', 'cn' placement in image)
peak_indices = [np.argmax(Va), np.argmax(Vb), np.argmax(Vc)]
peak_labels = ['an', 'bn', 'cn']
for idx, label in zip(peak_indices, peak_labels):
    # Only label peaks within the main cycle
    if 0 < t[idx] < 2*np.pi:
        ax[0].text(t[idx], np.max(Va) + 10, label, ha='center', fontweight='bold')


# --- BOTTOM PLOT: Bridge (Line-to-Line and DC Output) ---
# 1. Light background of ALL line-to-line combinations
line_to_line = [Vab, Vac, Vbc, Vba, Vca, Vcb]
line_colors = ['r', 'g', 'b', 'r', 'g', 'b'] # Cyclic pattern often used
for v, c in zip(line_to_line, line_colors):
    ax[1].plot(t, v, color=c, alpha=0.15, linestyle=':')

# 2. Highlight the specific DC Output Envelope (Vo)
# The calculation of Vdc_final ensures it traces the top.
# We will highlight the thick dark lines from the image.
for i in range(len(intervals) - 1):
    t_start = intervals[i] + np.pi/6
    t_end = intervals[i+1] + np.pi/6
    mask = (t >= t_start) & (t < t_end)
    
    # Highlight the conducting line voltage segment (thin)
    active_line = [Vab, Vac, Vbc, Vba, Vca, Vcb, Vab][i]
    ax[1].plot(t[mask], active_line[mask], color='k', linewidth=0.5, alpha=0.5)
    
    # Highlight the heavy Vdc (Vo) segments (matching the thick line in image)
    ax[1].plot(t[mask], Vdc_final[mask], color='k', linewidth=2.5, label='_nolegend_')

    # 3. Add Labels to Conduction Rectangles (Diodes + Lines)
    # Get center point for text
    t_mid = (t_start + t_end) / 2
    y_pos = np.mean(Vdc_final[mask]) - 20 # Sightly below envelope
    # Format text matching 'ab\n6,1' style
    text_content = f"${line_labels[i]}$\n{labels[i]}"
    ax[1].text(t_mid, y_pos, text_content, ha='center', va='top', fontweight='bold')


# --- AXIS FORMATTING & STYLING ---
# Shared X-axis settings
ax[1].set_xlabel('Electrical Angle ωt')
xticks = [0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3, 2*np.pi]
xticklabels = ['0', r'$\pi/3$', r'$2\pi/3$', r'$\pi$', r'$4\pi/3$', r'$5\pi/3$', r'$2\pi$']
ax[1].set_xticks(xticks)
ax[1].set_xticklabels(xticklabels)
ax[1].set_xlim(0, 2*np.pi)

# Final grid and title for the analysis
ax[1].grid(True, which='both', linestyle='--', alpha=0.5)
ax[1].set_title('Detailed Rectifier Analysis (Diode Conduction and output Vo)')

# Adjust spacing and display
plt.tight_layout()
st.pyplot(fig)
