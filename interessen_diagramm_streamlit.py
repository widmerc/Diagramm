import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(layout="wide")
st.title("Interessenpunkte Visualisierung")

uploaded_file = st.file_uploader("Excel-Datei hochladen (wie Vorlage)", type=["xlsx"])

if uploaded_file:
    excel_df = pd.read_excel(uploaded_file)
    interessen = excel_df['Interesse'].tolist()
    x_values = excel_df['x'].tolist()
    y_values = excel_df['y'].tolist()

    x_labels = {1: "privat", 2: "kommunal", 3: "kantonal", 4: "national", 5: "international"}
    y_labels = {1: "klein", 2: "mittel", 3: "gross"}
    color_bands = [
        "#ffffcc", "#ffeda0", "#fdbb84", "#fc9272", "#de2d26", "#a50f15", "#67000d",
    ]

    def fill_bands_between_lines(ax, lines, colors):
        num_bands = min(len(lines) - 1, len(colors))
        for i in range(num_bands):
            x_poly = [lines[i][0][0], lines[i][1][0], lines[i+1][1][0], lines[i+1][0][0]]
            y_poly = [lines[i][0][1], lines[i][1][1], lines[i+1][1][1], lines[i+1][0][1]]
            ax.fill(x_poly, y_poly, color=colors[i], zorder=0)

    def classify_points_in_bands(lines, x_values, y_values, labels):
        bands = []
        for xi, yi in zip(x_values, y_values):
            band_idx = None
            for i in range(len(lines) - 1):
                def interp_y(line, x):
                    x0, y0 = line[0]
                    x1, y1 = line[1]
                    if x1 == x0:
                        return max(y0, y1)
                    t = (x - x0) / (x1 - x0)
                    return y0 + t * (y1 - y0)
                y_top = interp_y(lines[i], xi)
                y_bottom = interp_y(lines[i+1], xi)
                if y_bottom <= yi <= y_top or y_top <= yi <= y_bottom:
                    band_idx = i
                    break
            bands.append(band_idx)
        return list(zip(labels, bands))

    from collections import defaultdict
    fig, axs = plt.subplots(1, 2, figsize=(16, 5.5))
    plt.subplots_adjust(wspace=0.35)
    ax = axs[0]
    lines = [
        [(0.1, 0), (0.1, 0)],
        [(3, 0), (0, 3)],
        [(3, 0), (0, 3)],
        [(4, 0), (0, 4)],
        [(5, 0), (0, 5)],
        [(6, 0), (0, 6)],
        [(7, 0), (0, 7)],
        [(9, 0), (0, 9)],
    ]
    fill_bands_between_lines(ax, lines, color_bands)
    classified = classify_points_in_bands(lines, x_values, y_values, interessen)
    band_dict = defaultdict(list)
    for label, band in classified:
        idx = interessen.index(label)
        band_dict[band].append((label, y_values[idx]))
    ax.scatter(x_values, y_values, s=400, color='black', alpha=0.5, zorder=2)
    for i, label in enumerate(interessen):
        ax.text(x_values[i], y_values[i], label, ha='center', va='center',
                fontsize=10, color='white', fontweight='bold', zorder=3)
    ax.set_xticks(list(x_labels.keys()))
    ax.set_xticklabels([x_labels[x] for x in x_labels])
    ax.set_yticks(list(y_labels.keys()))
    ax.set_yticklabels([y_labels[y] for y in y_labels])
    ax.set_xlabel("Bedeutung")
    ax.set_ylabel("Betroffenheit")
    ax.set_xlim(1, 5.2)
    ax.set_ylim(1, 3.2)
    ax.grid(False)
    ax.set_aspect("equal", adjustable='box')
    ax.set_title("Originaldiagramm")

    # Zweites Diagramm
    ax2 = axs[1]
    for i, color in enumerate(color_bands[1:], start=1):
        ax2.fill_betweenx([i+0.5, i+1.5], 0, i+1+0.5, color=color, zorder=0)
    for band, punkte in band_dict.items():
        if band is None or band == 0:
            continue
        y_band = band + 1
        n = len(punkte)
        x_min = 0.2
        x_max = band + 1 + 0.5 - 0.2
        if n == 1:
            x_offsets = [x_max]
        else:
            x_offsets = [x_max - i * (x_max - x_min) / (n - 1) for i in range(n)]
        for (label, _), x_plot in zip(punkte, x_offsets):
            ax2.scatter(x_plot, y_band, s=400, color='black', alpha=0.5, zorder=2)
            ax2.text(x_plot, y_band, label, ha='center', va='center',
                     fontsize=10, color='white', fontweight='bold', zorder=3)
    ax2.set_yticks([2, 4.5, 7])
    ax2.set_yticklabels(["klein", "öffentliches Interesse", "gross"])
    ax2.set_ylabel("Band")
    ax2.set_xlim(0.5, len(color_bands)+1.5)
    ax2.set_ylim(1.5, len(color_bands)+0.5)
    ax2.grid(False)
    ax2.set_aspect("auto")
    ax2.set_xticks([])
    ax2.set_xlabel("")
    ax2.tick_params(axis='y', which='both', length=0)

    st.pyplot(fig)

    # Download-Optionen für verschiedene PNG-Größen
    st.markdown("### Download-Optionen")
    size_option = st.selectbox(
        "PNG-Größe wählen:",
        ["Standard (1600x550)", "Groß (2400x825)", "Sehr groß (3200x1100)"]
    )
    dpi_map = {
        "Standard (1600x550)": 100,
        "Groß (2400x825)": 150,
        "Sehr groß (3200x1100)": 200
    }
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi_map[size_option])
    st.download_button(
        f"Diagramm als PNG herunterladen ({size_option})",
        data=buf.getvalue(),
        file_name="interessen_diagramm.png",
        mime="image/png"
    )

    
    st.markdown("### Geladene Daten (Vorschau)")
    st.dataframe(excel_df)

else:
    st.info("Bitte lade eine Excel-Datei im richtigen Format hoch.")