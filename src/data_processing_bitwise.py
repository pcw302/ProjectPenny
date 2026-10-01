from pathlib import Path
import numpy as np
import pandas as pd

PATH_DECKS = Path("data/decks/")
PATH_PROCESSED = Path("data/processed/")
PATH_RESULTS = PATH_PROCESSED / "results_bitwise.csv"

# Patterns represented as 3-bit integers (0 through 7)
PATTERNS = list(range(8))
MATCHUPS = [(p1, p2) for p1 in PATTERNS for p2 in PATTERNS if p1 != p2]


def pattern_to_string(pattern: int) -> str:
    """Converts 3-bit integer (e.g., 2 -> '010') to string 'BRB'."""
    return f"{pattern:03b}".replace("0", "B").replace("1", "R")


def string_to_pattern(pattern_str: str) -> int:
    """Converts pattern string 'BRB' back to 3-bit integer 2."""
    binary_str = pattern_str.replace("B", "0").replace("R", "1")
    return int(binary_str, 2)


def init_results_dict() -> dict:
    """Initializes empty counters for all 56 valid matchups."""
    results = {}
    for p1, p2 in MATCHUPS:
        results[(p1, p2)] = {
            "decks": 0,
            "hn_wins": 0, "hn_losses": 0, "hn_ties": 0,
            "ron_wins": 0, "ron_losses": 0, "ron_ties": 0,
        }
    return results


def load_existing_results() -> dict:
    """Loads existing raw counts from results_bitwise.csv if it exists."""
    results = init_results_dict()
    if not PATH_RESULTS.exists():
        return results

    try:
        df = pd.read_csv(PATH_RESULTS)
        for _, row in df.iterrows():
            p1 = string_to_pattern(row["my_choice"])
            p2 = string_to_pattern(row["opponent_choice"])
            matchup = (p1, p2)
            results[matchup] = {
                "decks": int(row["decks"]),
                "hn_wins": int(row["hn_wins"]),
                "hn_losses": int(row["hn_losses"]),
                "hn_ties": int(row["hn_ties"]),
                "ron_wins": int(row["ron_wins"]),
                "ron_losses": int(row["ron_losses"]),
                "ron_ties": int(row["ron_ties"]),
            }
    except Exception as e:
        print(f"[Warning] Could not parse existing CSV ({e}). Starting fresh.")
        results = init_results_dict()

    return results


def save_results(results: dict) -> None:
    """Saves accumulated results and pre-formatted cell annotations to CSV."""
    PATH_PROCESSED.mkdir(parents=True, exist_ok=True)

    rows = []
    for (p1_choice, p2_choice), scores in results.items():
        total_decks = scores["decks"]

        if total_decks > 0:
            hn_win_pct = round((scores["hn_wins"] / total_decks) * 100)
            hn_tie_pct = round((scores["hn_ties"] / total_decks) * 100)
            hn_label = f"{hn_win_pct}({hn_tie_pct})"

            ron_win_pct = round((scores["ron_wins"] / total_decks) * 100)
            ron_tie_pct = round((scores["ron_ties"] / total_decks) * 100)
            ron_label = f"{ron_win_pct}({ron_tie_pct})"
        else:
            hn_win_pct, hn_tie_pct, hn_label = 0, 0, "0(0)"
            ron_win_pct, ron_tie_pct, ron_label = 0, 0, "0(0)"

        rows.append({
            "my_choice": pattern_to_string(p1_choice),
            "opponent_choice": pattern_to_string(p2_choice),
            "decks": total_decks,
            "hn_wins": scores["hn_wins"],
            "hn_losses": scores["hn_losses"],
            "hn_ties": scores["hn_ties"],
            "ron_wins": scores["ron_wins"],
            "ron_losses": scores["ron_losses"],
            "ron_ties": scores["ron_ties"],
            "hn_win_pct": hn_win_pct,
            "hn_tie_pct": hn_tie_pct,
            "ron_win_pct": ron_win_pct,
            "ron_tie_pct": ron_tie_pct,
            "hn_label": hn_label,
            "ron_label": ron_label,
        })

    df = pd.DataFrame(rows)
    df.to_csv(PATH_RESULTS, index=False)


def process_deck_file(filepath: Path, results: dict) -> None:
    """Processes a single .npy deck file using high-speed C byte indexing."""
    decks = np.load(filepath)

    for deck in decks:
        # Pre-calculate 50 3-bit window integers directly into C bytes
        windows_bytes = bytes((deck[:-2] << 2) | (deck[1:-1] << 1) | deck[2:])

        for p1, p2 in MATCHUPS:
            p1_tricks = p2_tricks = p1_cards = p2_cards = 0
            idx = 0
            cards_in_pile = 3

            while idx < 50:
                val = windows_bytes[idx]
                if val == p1:
                    p1_tricks += 1
                    p1_cards += cards_in_pile
                    idx += 3
                    cards_in_pile = 3
                elif val == p2:
                    p2_tricks += 1
                    p2_cards += cards_in_pile
                    idx += 3
                    cards_in_pile = 3
                else:
                    idx += 1
                    cards_in_pile += 1

            res = results[(p1, p2)]
            res["decks"] += 1

            # Tricks Scoring
            if p1_tricks > p2_tricks:
                res["hn_wins"] += 1
            elif p1_tricks < p2_tricks:
                res["hn_losses"] += 1
            else:
                res["hn_ties"] += 1

            # Cards Scoring
            if p1_cards > p2_cards:
                res["ron_wins"] += 1
            elif p1_cards < p2_cards:
                res["ron_losses"] += 1
            else:
                res["ron_ties"] += 1


def process_new_decks(new_filepaths: list[Path]) -> int:
    """Loads existing CSV counts, processes ONLY the new deck file(s), and updates CSV."""
    results = load_existing_results()

    for fp in new_filepaths:
        print(f"  -> Processing new file: {fp.name}...")
        process_deck_file(fp, results)

    save_results(results)
    first_key = list(results.keys())[0]
    return results[first_key]["decks"]


def process_all_decks() -> int:
    """Reprocesses ALL deck files in data/decks/ from scratch."""
    results = init_results_dict()
    deck_files = sorted(PATH_DECKS.glob("*.npy"))

    if not deck_files:
        return 0

    for filepath in deck_files:
        print(f"  -> Processing file: {filepath.name}...")
        process_deck_file(filepath, results)

    save_results(results)
    first_key = list(results.keys())[0]
    return results[first_key]["decks"]