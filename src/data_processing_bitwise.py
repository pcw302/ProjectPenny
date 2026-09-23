from pathlib import Path
import numpy as np
import pandas as pd

PATH_DECKS = Path("data/decks/")
PATH_PROCESSED = Path("data/processed/")
PATH_RESULTS = PATH_PROCESSED / "results_bitwise.csv"

# Patterns represented as 3-bit integers (0 through 7)
PATTERNS = list(range(8))

def pattern_to_string(pattern: int) -> str:
    """Converts 3-bit integer (e.g., 2 -> '010') to string 'BRB'."""
    return f"{pattern:03b}".replace("0", "B").replace("1", "R")

def string_to_pattern(pattern_str: str) -> int:
    """Converts pattern string 'BRB' back to 3-bit integer 2."""
    binary_str = pattern_str.replace("B", "0").replace("R", "1")
    return int(binary_str, 2)

def play_game(
    windows: np.ndarray, 
    p1_choice: int, 
    p2_choice: int
) -> tuple:
    """Simulates one game using pre-computed 3-bit integer array windows."""
    p1_tricks, p2_tricks = 0, 0
    p1_cards, p2_cards = 0, 0
    
    idx = 0
    cards_in_pile = 3
    num_windows = len(windows)

    while idx < num_windows:
        val = windows[idx]
        if val == p1_choice:
            p1_tricks += 1
            p1_cards += cards_in_pile
            idx += 3  # Clear pile: advance past the 3 used cards
            cards_in_pile = 3
        elif val == p2_choice:
            p2_tricks += 1
            p2_cards += cards_in_pile
            idx += 3  # Clear pile: advance past the 3 used cards
            cards_in_pile = 3
        else:
            idx += 1
            cards_in_pile += 1

    return p1_tricks, p2_tricks, p1_cards, p2_cards

def init_results_dict() -> dict:
    """Initializes empty counters for all 56 valid matchups."""
    results = {}
    for p1_choice in PATTERNS:
        for p2_choice in PATTERNS:
            if p1_choice == p2_choice:
                continue
            results[(p1_choice, p2_choice)] = {
                "decks": 0,
                "hn_wins": 0, "hn_losses": 0, "hn_ties": 0,
                "ron_wins": 0, "ron_losses": 0, "ron_ties": 0,
            }
    return results

def process_deck(deck: np.ndarray, results: dict) -> None:
    """Evaluates one deck across all 56 valid matchups using bitwise windows."""
    # Pre-calculate 50 3-bit window integers in C-speed via NumPy vectorization
    windows = (deck[:-2] << 2) | (deck[1:-1] << 1) | deck[2:]

    for p1_choice in PATTERNS:
        for p2_choice in PATTERNS:
            if p1_choice == p2_choice:
                continue

            matchup = (p1_choice, p2_choice)
            p1_tricks, p2_tricks, p1_cards, p2_cards = play_game(
                windows, p1_choice, p2_choice
            )

            results[matchup]["decks"] += 1

            if p1_tricks > p2_tricks:
                results[matchup]["hn_wins"] += 1
            elif p1_tricks < p2_tricks:
                results[matchup]["hn_losses"] += 1
            else:
                results[matchup]["hn_ties"] += 1

            if p1_cards > p2_cards:
                results[matchup]["ron_wins"] += 1
            elif p1_cards < p2_cards:
                results[matchup]["ron_losses"] += 1
            else:
                results[matchup]["ron_ties"] += 1
                
                
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


def process_all_decks() -> int:
    """Processes all deck files in data/decks/ using bitwise processing and saves results."""
    results = init_results_dict()
    deck_files = sorted(PATH_DECKS.glob("*.npy"))
    
    if not deck_files:
        return 0

    for filepath in deck_files:
        decks = np.load(filepath)
        for deck in decks:
            process_deck(deck, results)

    save_results(results)
    first_key = list(results.keys())[0]
    return results[first_key]["decks"]