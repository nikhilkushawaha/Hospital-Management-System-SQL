# =============================================================================
# visualizations.py — Hospital Analytics Pipeline: Chart Generation
# =============================================================================
# All Matplotlib/Seaborn chart functions live here.
# Each function saves a PNG to the /visuals folder AND returns the figure
# so it renders inline in the Jupyter notebook.
# =============================================================================

import os
import warnings
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

from config import VISUALS_DIR, FIGURE_DPI, FIGURE_STYLE, COLOR_PALETTE

warnings.filterwarnings("ignore", category=FutureWarning)

# ── Global style setup ────────────────────────────────────────────────────────
try:
    plt.style.use(FIGURE_STYLE)
except OSError:
    plt.style.use("seaborn-v0_8-whitegrid")   # fallback for older matplotlib

sns.set_palette(COLOR_PALETTE)

# Ensure visuals directory exists
os.makedirs(VISUALS_DIR, exist_ok=True)

# Typography
TITLE_FONTSIZE  = 15
LABEL_FONTSIZE  = 11
TICK_FONTSIZE   = 9
ANNOT_FONTSIZE  = 9
ACCENT_COLOR    = "#4C72B0"
SECONDARY_COLOR = "#DD8452"


def _save(fig: plt.Figure, filename: str) -> str:
    """Save figure to /visuals and return the full path."""
    path = os.path.join(VISUALS_DIR, filename)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    print(f"[viz] Saved --> {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Top Diagnoses Bar Chart
# ─────────────────────────────────────────────────────────────────────────────

def plot_top_diagnoses(diagnosis_freq_df: pd.DataFrame,
                        top_n: int = 10,
                        filename: str = "top_diagnoses.png") -> plt.Figure:
    """
    Horizontal bar chart of the most frequent diagnoses.

    Args:
        diagnosis_freq_df: output of insights.diagnosis_frequency()
        top_n:             how many diagnoses to show
        filename:          output filename inside /visuals

    Returns:
        matplotlib Figure (also saved to disk)
    """
    df = diagnosis_freq_df.head(top_n).sort_values("count")

    palette = sns.color_palette("Blues_d", len(df))

    fig, ax = plt.subplots(figsize=(11, 6))

    bars = ax.barh(
        df["diagnosis"],
        df["count"],
        color=palette,
        edgecolor="white",
        linewidth=0.6,
        height=0.65,
    )

    # Annotate bars with count
    for bar, count in zip(bars, df["count"]):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            str(int(count)),
            va="center",
            ha="left",
            fontsize=ANNOT_FONTSIZE,
            color="#333333",
        )

    ax.set_xlabel("Number of Cases", fontsize=LABEL_FONTSIZE)
    ax.set_title(
        f"Top {top_n} Most Frequent Diagnoses\nHospital Patient Records",
        fontsize=TITLE_FONTSIZE,
        fontweight="bold",
        pad=14,
    )
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_xlim(0, df["count"].max() * 1.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=TICK_FONTSIZE)
    plt.tight_layout()

    _save(fig, filename)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Physician Workload Bar Chart
# ─────────────────────────────────────────────────────────────────────────────

def plot_physician_workload(workload_df: pd.DataFrame,
                             top_n: int = 15,
                             filename: str = "physician_workload.png") -> plt.Figure:
    """
    Grouped bar chart: diagnoses handled vs. primary patients per physician.

    Args:
        workload_df: output of insights.physician_workload_combined()
        top_n:       physicians to show (ranked by diagnoses)
        filename:    output filename inside /visuals

    Returns:
        matplotlib Figure
    """
    df = workload_df.head(top_n).copy()

    # Shorten physician names: "Dr.John Dorian" → "J. Dorian"
    def shorten(name: str) -> str:
        parts = name.replace("Dr.", "").strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}. {parts[-1]}"
        return name

    df["short_name"] = df["physician_name"].apply(shorten)
    df = df.sort_values("diagnoses_handled", ascending=False)

    x = range(len(df))
    width = 0.38

    fig, ax = plt.subplots(figsize=(14, 6))

    b1 = ax.bar(
        [i - width / 2 for i in x],
        df["diagnoses_handled"],
        width=width,
        label="Diagnoses Handled",
        color=ACCENT_COLOR,
        edgecolor="white",
    )
    b2 = ax.bar(
        [i + width / 2 for i in x],
        df["primary_patients"],
        width=width,
        label="Primary Care Patients",
        color=SECONDARY_COLOR,
        edgecolor="white",
    )

    # Value labels on bars
    for bars in [b1, b2]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h + 0.08,
                    str(int(h)),
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#333333",
                )

    ax.set_xticks(list(x))
    ax.set_xticklabels(df["short_name"], rotation=40, ha="right",
                        fontsize=TICK_FONTSIZE)
    ax.set_ylabel("Count", fontsize=LABEL_FONTSIZE)
    ax.set_title(
        f"Physician Workload — Top {top_n} Physicians\n"
        "Diagnoses Handled vs. Primary Care Patients",
        fontsize=TITLE_FONTSIZE,
        fontweight="bold",
        pad=14,
    )
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.legend(fontsize=LABEL_FONTSIZE)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    _save(fig, filename)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Procedure Cost Distribution (Histogram + Boxplot)
# ─────────────────────────────────────────────────────────────────────────────

def plot_procedure_cost_distribution(procedures_df: pd.DataFrame,
                                      filename: str = "procedure_cost_distribution.png") -> plt.Figure:
    """
    Side-by-side: histogram of procedure costs + horizontal boxplot.
    Also includes a ranked dot-plot of individual procedures.

    Args:
        procedures_df: raw procedures DataFrame
        filename:      output filename inside /visuals

    Returns:
        matplotlib Figure
    """
    costs = procedures_df["cost"]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # ── Panel 1: Histogram ─────────────────────────────────────────────────
    ax1 = axes[0]
    ax1.hist(
        costs,
        bins=8,
        color=ACCENT_COLOR,
        edgecolor="white",
        linewidth=0.8,
        alpha=0.88,
    )
    ax1.axvline(costs.mean(), color="#E74C3C", linestyle="--", linewidth=1.5,
                label=f"Mean: ₹{costs.mean():,.0f}")
    ax1.axvline(costs.median(), color="#27AE60", linestyle=":", linewidth=1.5,
                label=f"Median: ₹{costs.median():,.0f}")
    ax1.set_xlabel("Cost (₹)", fontsize=LABEL_FONTSIZE)
    ax1.set_ylabel("Frequency", fontsize=LABEL_FONTSIZE)
    ax1.set_title("Cost Distribution\n(Histogram)", fontsize=TITLE_FONTSIZE,
                   fontweight="bold")
    ax1.legend(fontsize=8)
    ax1.spines[["top", "right"]].set_visible(False)

    # ── Panel 2: Boxplot ───────────────────────────────────────────────────
    ax2 = axes[1]
    bp = ax2.boxplot(
        costs,
        vert=False,
        patch_artist=True,
        boxprops=dict(facecolor=ACCENT_COLOR, alpha=0.7),
        medianprops=dict(color="#27AE60", linewidth=2),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker="o", color=SECONDARY_COLOR, markersize=6),
    )
    ax2.set_xlabel("Cost (₹)", fontsize=LABEL_FONTSIZE)
    ax2.set_title("Cost Spread\n(Box Plot)", fontsize=TITLE_FONTSIZE,
                   fontweight="bold")
    ax2.set_yticks([])
    ax2.spines[["top", "right", "left"]].set_visible(False)

    # ── Panel 3: Ranked dot/bar per procedure ──────────────────────────────
    ax3 = axes[2]
    sorted_procs = procedures_df[["name", "cost"]].sort_values("cost")
    short_names = sorted_procs["name"].apply(
        lambda n: n[:22] + "…" if len(n) > 22 else n
    )
    palette3 = sns.color_palette("coolwarm", len(sorted_procs))
    ax3.barh(short_names, sorted_procs["cost"], color=palette3, height=0.65)
    ax3.set_xlabel("Cost (₹)", fontsize=LABEL_FONTSIZE)
    ax3.set_title("Cost by Procedure\n(Catalog)", fontsize=TITLE_FONTSIZE,
                   fontweight="bold")
    ax3.tick_params(axis="y", labelsize=7)
    ax3.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Medical Procedure Cost Analysis",
        fontsize=TITLE_FONTSIZE + 2,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()

    _save(fig, filename)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4.  Patient Gender Distribution (Pie + Bar)
# ─────────────────────────────────────────────────────────────────────────────

def plot_gender_distribution(gender_df: pd.DataFrame,
                              filename: str = "patient_gender_distribution.png") -> plt.Figure:
    """
    Side-by-side pie chart and bar chart for patient gender distribution.

    Args:
        gender_df: output of insights.gender_distribution()
        filename:  output filename inside /visuals

    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    colors = ["#4C72B0", "#DD8452"]
    labels = gender_df["gender"].tolist()
    counts = gender_df["count"].tolist()
    pcts   = gender_df["percentage"].tolist()

    # ── Pie chart ─────────────────────────────────────────────────────────
    ax1 = axes[0]
    wedges, texts, autotexts = ax1.pie(
        counts,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=LABEL_FONTSIZE),
    )
    for at in autotexts:
        at.set_fontsize(12)
        at.set_fontweight("bold")
    ax1.set_title("Gender Distribution\n(Pie Chart)", fontsize=TITLE_FONTSIZE,
                   fontweight="bold")

    # ── Bar chart ─────────────────────────────────────────────────────────
    ax2 = axes[1]
    bars = ax2.bar(labels, counts, color=colors, edgecolor="white",
                    linewidth=1.5, width=0.45)

    for bar, count, pct in zip(bars, counts, pcts):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            f"{count}\n({pct}%)",
            ha="center",
            va="bottom",
            fontsize=LABEL_FONTSIZE,
            fontweight="bold",
        )

    ax2.set_ylabel("Number of Patients", fontsize=LABEL_FONTSIZE)
    ax2.set_title("Gender Distribution\n(Bar Chart)", fontsize=TITLE_FONTSIZE,
                   fontweight="bold")
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax2.set_ylim(0, max(counts) * 1.25)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Patient Gender Distribution — 39 Patients",
        fontsize=TITLE_FONTSIZE + 2,
        fontweight="bold",
    )
    plt.tight_layout()

    _save(fig, filename)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5.  Bonus: Diagnoses by Department Heatmap-style Bar
# ─────────────────────────────────────────────────────────────────────────────

def plot_diagnoses_by_department(dept_diag_df: pd.DataFrame,
                                  filename: str = "diagnoses_by_department.png") -> plt.Figure:
    """
    Horizontal bar chart of diagnosis counts per department.

    Args:
        dept_diag_df: output of insights.diagnosis_by_department()
        filename:     output filename inside /visuals

    Returns:
        matplotlib Figure
    """
    df = dept_diag_df.dropna(subset=["department_name"]).sort_values("diagnosis_count")

    palette = sns.color_palette("viridis", len(df))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(
        df["department_name"],
        df["diagnosis_count"],
        color=palette,
        edgecolor="white",
        height=0.65,
    )

    for bar, count in zip(bars, df["diagnosis_count"]):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            str(int(count)),
            va="center",
            ha="left",
            fontsize=ANNOT_FONTSIZE,
            color="#333333",
        )

    ax.set_xlabel("Number of Diagnoses Handled", fontsize=LABEL_FONTSIZE)
    ax.set_title(
        "Diagnoses by Department\n(via Physician Primary Affiliation)",
        fontsize=TITLE_FONTSIZE,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlim(0, df["diagnosis_count"].max() * 1.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=TICK_FONTSIZE)
    plt.tight_layout()

    _save(fig, filename)
    return fig
