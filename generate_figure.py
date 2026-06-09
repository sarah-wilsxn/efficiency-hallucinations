"""
Generates calibration_figure.pdf — per-model abstention rate bar chart.
Run from the efficiency-hallucinations directory:
    python generate_figure.py
Requires matplotlib.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

MODELS = [
    ("Claude Opus 4.7-Fast",   60,  "Claude"),
    ("Claude Opus 4.8",        40,  "Claude"),
    ("Claude Sonnet 4.5",      60,  "Claude"),
    ("Gemini 3 Flash Preview", 60,  "Gemini"),
    ("Gemini 3.1 Pro Preview", 20,  "Gemini"),
    ("Gemini 3.5 Flash",        0,  "Gemini"),
    ("GPT-5 Mini",             40,  "GPT"),
    ("GPT-5.4",                20,  "GPT"),
    ("GPT-5.4 Mini",          100,  "GPT"),
]

FAMILY_COLORS = {
    "Claude": "#C0392B",
    "Gemini": "#2980B9",
    "GPT":    "#27AE60",
}

OVERALL_AVG = 44.4

labels  = [m[0] for m in MODELS]
values  = [m[1] for m in MODELS]
colors  = [FAMILY_COLORS[m[2]] for m in MODELS]

fig, ax = plt.subplots(figsize=(5.5, 4.2))

bars = ax.barh(labels, values, color=colors, edgecolor="white", height=0.6)

for bar, val in zip(bars, values):
    x_pos = val + 1.5 if val < 95 else val - 3.5
    ha    = "left"    if val < 95 else "right"
    color = "black"   if val < 95 else "white"
    ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
            f"{val}%", va="center", ha=ha, fontsize=8, color=color, fontweight="bold")

ax.axvline(OVERALL_AVG, color="black", linestyle="--", linewidth=1.2, label=f"Overall Avg. ({OVERALL_AVG:.1f}%)")

ax.set_xlim(0, 115)
ax.set_xlabel("Calibrated Abstention Rate (%)", fontsize=9)
ax.set_title("Per-Model Abstention Rate on Optimal Code\n(IIV Penalty Condition)", fontsize=9, pad=6)
ax.tick_params(axis="y", labelsize=8)
ax.tick_params(axis="x", labelsize=8)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

legend_patches = [mpatches.Patch(color=c, label=f) for f, c in FAMILY_COLORS.items()]
legend_patches.append(
    plt.Line2D([0], [0], color="black", linestyle="--", linewidth=1.2, label=f"Overall Avg. ({OVERALL_AVG:.1f}%)")
)
ax.legend(handles=legend_patches, fontsize=7.5, loc="lower right", framealpha=0.9)

plt.tight_layout()
plt.savefig("calibration_figure.pdf", bbox_inches="tight", dpi=300)
plt.savefig("calibration_figure.png", bbox_inches="tight", dpi=200)
print("Saved calibration_figure.pdf and calibration_figure.png")
