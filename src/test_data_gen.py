import json
import pandas as pd
from pathlib import Path

# 1. Verify seed log file
seed_path = Path("data/seed.json")
assert seed_path.exists(), "FAIL: seed.json was not created!"
with seed_path.open("r") as f:
    seed_info = json.load(f)
    print(f"Current logged seed: {seed_info['seed']}")

# 2. Find and read the most recently generated deck file
deck_files = list(Path("data/decks/").glob("*.jsonl"))
assert len(deck_files) > 0, "FAIL: No deck files found in data/decks/!"

latest_file = max(deck_files, key=lambda p: p.stat().st_mtime)
print(f"Testing file: {latest_file.name}")

df = pd.read_json(latest_file, lines=True)

# 3. Assert correct structure and card distribution across all generated decks
assert "deck" in df.columns, "FAIL: Column 'deck' missing from jsonl structure!"

for idx, row in df.iterrows():
    deck = row["deck"]
    
    # Check total card count
    assert len(deck) == 52, f"FAIL Deck {idx}: Expected 52 cards, got {len(deck)}"
    
    # Check exact card breakdown (26 zeros, 26 ones)
    count_0 = deck.count(0)
    count_1 = deck.count(1)
    assert count_0 == 26 and count_1 == 26, (
        f"FAIL Deck {idx}: Invalid ratio ({count_0} zeros, {count_1} ones)"
    )

print("PASS: All generated decks are structurally valid, equal-ratio 52-card decks!")