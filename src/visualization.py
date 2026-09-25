from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PATH_RESULTS = Path("data/processed/results_bitwise.csv")
PATH_FIGURES = Path("figures/")
LABELS = ["BBB", "BBR", "BRB", "BRR", "RBB", "RBR", "RRB", "RRR"]


def plot_heatmaps() -> None:
    """Generates, saves to figures/, and displays side-by-side heatmaps for Tricks and Cards scoring."""
    if not PATH_RESULTS.exists():
        print(f"\n[Error] Results file not found at '{PATH_RESULTS}'.")
        print("Please simulate decks first using Option 2 in the CLI.")
        return

    df = pd.read_csv(PATH_RESULTS)

    if df.empty or "decks" not in df.columns:
        print("\n[Error] Results file is empty or malformed.")
        return

    total_decks = int(df["decks"].iloc[0])

    # 1. Pivot matrices for Win Percentages (Coloring)
    hn_win = df.pivot(
        index="opponent_choice", columns="my_choice", values="hn_win_pct"
    ).reindex(index=LABELS, columns=LABELS)

    ron_win = df.pivot(
        index="opponent_choice", columns="my_choice", values="ron_win_pct"
    ).reindex(index=LABELS, columns=LABELS)

    # 2. Pivot matrices for Cell Text "Win%(Tie%)"
    hn_label = (
        df.pivot(
            index="opponent_choice", columns="my_choice", values="hn_label"
        )
        .reindex(index=LABELS, columns=LABELS)
        .fillna("")
    )

    ron_label = (
        df.pivot(
            index="opponent_choice", columns="my_choice", values="ron_label"
        )
        .reindex(index=LABELS, columns=LABELS)
        .fillna("")
    )

    # Diagonal mask to gray out matching choices
    mask = np.eye(8, dtype=bool)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Set light gray background for diagonal cells on both subplots
    axes[0].set_facecolor("#cccccc")
    axes[1].set_facecolor("#cccccc")

    # Heatmap 1: Scoring by Tricks (Humble-Nishiyama)
    sns.heatmap(
        hn_win,
        annot=hn_label,
        fmt="",
        cmap="Blues",
        cbar=False,
        ax=axes[0],
        mask=mask,
        linewidths=1.5,
        linecolor="white",
        annot_kws={"size": 9.5},
        vmin=0,
        vmax=100,
    )
    axes[0].set_title(
        f"My Probability of Win(Tie)\nScoring By [Tricks]\nN={total_decks:,}",
        fontsize=12,
        pad=12,
    )
    axes[0].set_xlabel("My Choice", fontsize=11, labelpad=8)
    axes[0].set_ylabel("Opponent Choice", fontsize=11, labelpad=8)

    # Heatmap 2: Scoring by Cards (Ron's Variation)
    sns.heatmap(
        ron_win,
        annot=ron_label,
        fmt="",
        cmap="Blues",
        cbar=False,
        ax=axes[1],
        mask=mask,
        linewidths=1.5,
        linecolor="white",
        annot_kws={"size": 9.5},
        vmin=0,
        vmax=100,
    )
    axes[1].set_title(
        f"My Probability of Win(Tie)\nScoring By [Cards]\nN={total_decks:,}",
        fontsize=12,
        pad=12,
    )
    axes[1].set_xlabel("My Choice", fontsize=11, labelpad=8)
    axes[1].set_ylabel("Opponent Choice", fontsize=11, labelpad=8)

    plt.tight_layout()

    # Ensure figures directory exists and save before showing
    PATH_FIGURES.mkdir(parents=True, exist_ok=True)
    save_path = PATH_FIGURES / "heatmaps_tricks_vs_cards.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"\nHeatmap figure successfully saved to: {save_path}")

    plt.show()


if __name__ == "__main__":
    plot_heatmaps()