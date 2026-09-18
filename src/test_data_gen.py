import json
import numpy as np
from pathlib import Path

def test_data_generation():
    # 1. Verify seed log file
    seed_path = Path("data/seed.json")
    assert seed_path.exists(), "FAIL: seed.json was not created!"
    with seed_path.open("r") as f:
        seed_info = json.load(f)
        print(f"Current logged seed: {seed_info['seed']}")

    # 2. Find and read the most recent .npy deck file
    deck_files = list(Path("data/decks/").glob("*.npy"))
    assert len(deck_files) > 0, "FAIL: No .npy deck files found in data/decks/!"

    latest_file = max(deck_files, key=lambda p: p.stat().st_mtime)
    print(f"Testing file: {latest_file.name}")

    # Load binary array directly into memory
    decks = np.load(latest_file)

    # 3. Assert shape, data type, and card counts
    assert decks.ndim == 2, "FAIL: Decks array is not 2-dimensional!"
    assert decks.shape[1] == 52, f"FAIL: Expected 52 cards per deck, got {decks.shape[1]}"
    assert decks.dtype == np.uint8, f"FAIL: Expected uint8 dtype, got {decks.dtype}"

    # Verify card distribution across all decks (vectorized sum check)
    red_counts = np.sum(decks == 1, axis=1)
    black_counts = np.sum(decks == 0, axis=1)

    assert np.all(red_counts == 26), "FAIL: Some decks do not contain exactly 26 red cards!"
    assert np.all(black_counts == 26), "FAIL: Some decks do not contain exactly 26 black cards!"

    print("PASS: All generated decks are structurally valid 52-card decks with 1:1 color ratio!")

if __name__ == "__main__":
    test_data_generation()