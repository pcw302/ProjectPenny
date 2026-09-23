from pathlib import Path
import numpy as np
import pandas as pd

# File paths
PATH_DECKS = Path("data/decks/")
PATH_PROCESSED = Path("data/processed/")
PATH_RESULTS = PATH_PROCESSED / "results.csv"

# All 8 possible three-card patterns (0 = Black, 1 = Red)
PATTERNS = [
    (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
    (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1),
]

def pattern_to_string(pattern: tuple) -> str:
    """Converts numeric tuple (0, 1, 1) to string 'BRR'."""
    return "".join("B" if card == 0 else "R" for card in pattern)

def string_to_pattern(pattern_str: str) -> tuple:
    """Converts string 'BRR' back to numeric tuple (0, 1, 1)."""
    return tuple(0 if char == "B" else 1 for char in pattern_str)

def play_game(
    deck: np.ndarray, 
    my_choice: tuple, 
    opponent_choice: tuple
) -> tuple:
    """
    Simulates one deck for a pair of player choices.

    Returns:
        my_tricks: Number of tricks won by Player 1 (Me).
        opponent_tricks: Number of tricks won by Opponent.
        my_cards: Total number of cards won by Player 1 (Me).
        opponent_cards: Total number of cards won by Opponent.
    """
    my_tricks, opponent_tricks = 0, 0
    my_cards, opponent_cards = 0, 0
    current_pile = []

    for card in deck:
        current_pile.append(card)
        if len(current_pile) < 3:
            continue

        last_three = tuple(current_pile[-3:])
        if last_three == my_choice:
            my_tricks += 1
            my_cards += len(current_pile)
            current_pile = []
        elif last_three == opponent_choice:
            opponent_tricks += 1
            opponent_cards += len(current_pile)
            current_pile = []

    return my_tricks, opponent_tricks, my_cards, opponent_cards

def init_results_dict() -> dict:
    """Initializes clean, empty counters for all 56 valid matchups."""
    results = {}
    for my_choice in PATTERNS:
        for opponent_choice in PATTERNS:
            if my_choice == opponent_choice:
                continue
            results[(my_choice, opponent_choice)] = {
                "decks": 0,
                "hn_wins": 0, "hn_losses": 0, "hn_ties": 0,
                "ron_wins": 0, "ron_losses": 0, "ron_ties": 0,
            }
    return results

def load_or_create_results() -> dict:
    """
    Loads accumulated results from results.csv if present, 
    otherwise initializes empty counters for all 56 valid matchups.
    """
    results = init_results_dict()

    if PATH_RESULTS.exists():
        df = pd.read_csv(PATH_RESULTS)
        for _, row in df.iterrows():
            my_choice = string_to_pattern(row["my_choice"])
            opp_choice = string_to_pattern(row["opponent_choice"])
            matchup = (my_choice, opp_choice)

            if matchup in results:
                results[matchup]["decks"] = int(row["decks"])
                results[matchup]["hn_wins"] = int(row["hn_wins"])
                results[matchup]["hn_losses"] = int(row["hn_losses"])
                results[matchup]["hn_ties"] = int(row["hn_ties"])
                results[matchup]["ron_wins"] = int(row["ron_wins"])
                results[matchup]["ron_losses"] = int(row["ron_losses"])
                results[matchup]["ron_ties"] = int(row["ron_ties"])

    return results

def process_deck(deck: np.ndarray, results: dict) -> None:
    """Evaluates one deck across all 56 valid matchups."""
    for my_choice in PATTERNS:
        for opponent_choice in PATTERNS:
            if my_choice == opponent_choice:
                continue

            matchup = (my_choice, opponent_choice)
            my_tricks, opp_tricks, my_cards, opp_cards = play_game(
                deck, my_choice, opponent_choice
            )

            results[matchup]["decks"] += 1

            # Version 1: Humble-Nishiyama Game scoring (Tricks)
            if my_tricks > opp_tricks:
                results[matchup]["hn_wins"] += 1
            elif my_tricks < opp_tricks:
                results[matchup]["hn_losses"] += 1
            else:
                results[matchup]["hn_ties"] += 1

            # Version 2: Ron's Variation scoring (Total Cards)
            if my_cards > opp_cards:
                results[matchup]["ron_wins"] += 1
            elif my_cards < opp_cards:
                results[matchup]["ron_losses"] += 1
            else:
                results[matchup]["ron_ties"] += 1

def process_file(filepath: Path, results: dict) -> None:
    """Loads a .npy binary deck file and processes all contained decks."""
    print(f"Processing {filepath}...")
    decks = np.load(filepath)
    for deck in decks:
        process_deck(deck, results)
    print(f"Completed {len(decks):,} decks from {filepath.name}.")

def save_results(results: dict) -> None:
    """
    Saves accumulated results and pre-calculated win/tie percentages and display strings 
    to data/processed/results.csv for direct plotting.
    """
    PATH_PROCESSED.mkdir(parents=True, exist_ok=True)
    
    rows = []
    for (my_choice, opponent_choice), scores in results.items():
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
            "my_choice": pattern_to_string(my_choice),
            "opponent_choice": pattern_to_string(opponent_choice),
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
    print(f"Results saved to {PATH_RESULTS}")

if __name__ == "__main__":
    results = load_or_create_results()
    deck_files = sorted(PATH_DECKS.glob("*.npy"))
    
    if not deck_files:
        print("No .npy deck files found in data/decks/. Run data_generation.py first.")
    else:
        for filepath in deck_files:
            process_file(filepath, results)
        save_results(results)