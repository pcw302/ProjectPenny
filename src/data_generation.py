from pathlib import Path
import re
import numpy as np

PATH_DECKS = Path("data/decks/")

def get_next_seed() -> int:
    """Scans existing .npy files in data/decks/ and returns the next sequential seed."""
    if not PATH_DECKS.exists():
        return 1

    deck_files = list(PATH_DECKS.glob("*.npy"))
    if not deck_files:
        return 1

    seeds = []
    for filepath in deck_files:
        # Regex captures seed integer from filenames like 'decks_seed_42.npy' or 'decks_seed_42_part1.npy'
        match = re.search(r"seed_(\d+)", filepath.stem)
        if match:
            seeds.append(int(match.group(1)))

    return max(seeds) + 1 if seeds else 1

def make_decks(seed: int, n_decks: int) -> np.ndarray:
    """
    Generates a 2D NumPy array of shape (n_decks, 52).
    Each deck consists of 26 zeros (Black) and 26 ones (Red) shuffled using the seed.
    """
    rng = np.random.default_rng(seed)
    
    # Base 52-card standard deck (26 Black = 0, 26 Red = 1)
    base_deck = np.array([0] * 26 + [1] * 26, dtype=np.uint8)

    # Pre-allocate 2D array
    decks = np.empty((n_decks, 52), dtype=np.uint8)
    for i in range(n_decks):
        deck = base_deck.copy()
        rng.shuffle(deck)
        decks[i] = deck

    return decks

def save_decks_npy(decks: np.ndarray, seed: int, max_mb: float = 45.0) -> list[Path]:
    """
    Saves decks to .npy files in data/decks/.
    Chunks the array into multiple files if it exceeds max_mb (default 45 MB)
    to safely stay under GitHub's file size limits.
    """
    PATH_DECKS.mkdir(parents=True, exist_ok=True)

    max_bytes = int(max_mb * 1024 * 1024)
    bytes_per_deck = decks.shape[1] * decks.itemsize  # 52 bytes for uint8
    
    # Calculate maximum decks per file (leaving 256 bytes room for NumPy header)
    max_decks_per_file = max(1, (max_bytes - 256) // bytes_per_deck)
    total_decks = len(decks)
    saved_paths = []

    # Case 1: Fits comfortably in a single file
    if total_decks <= max_decks_per_file:
        filepath = PATH_DECKS / f"decks_seed_{seed}.npy"
        np.save(filepath, decks)
        saved_paths.append(filepath)
        print(f"Saved {total_decks:,} decks to {filepath} ({filepath.stat().st_size / (1024*1024):.2f} MB)")
    
    # Case 2: Exceeds 45 MB, chunk into parts
    else:
        num_chunks = int(np.ceil(total_decks / max_decks_per_file))
        print(f"\nTotal decks exceed {max_mb:.0f} MB target limit. Chunking into {num_chunks} files...")

        for part_idx in range(num_chunks):
            start_idx = part_idx * max_decks_per_file
            end_idx = min((part_idx + 1) * max_decks_per_file, total_decks)
            chunk = decks[start_idx:end_idx]

            filepath = PATH_DECKS / f"decks_seed_{seed}_part{part_idx + 1}.npy"
            np.save(filepath, chunk)
            saved_paths.append(filepath)
            
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  -> Part {part_idx + 1}/{num_chunks}: Saved {len(chunk):,} decks to {filepath} ({size_mb:.2f} MB)")

    return saved_paths