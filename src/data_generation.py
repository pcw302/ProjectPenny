import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# Define file paths and constants
PATH_DECKS = Path('data/decks/')
PATH_SEED_LOG = Path('data/seed.json')
SEED_BASE = 1
CARDS_PER_COLOR = 26

def get_next_seed() -> int:
    """
    Reads the last seed used from seed.json, increments it by 1, 
    and updates the log file. Creates a new log if one does not exist.
    """
    PATH_SEED_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine the next seed
    if not PATH_SEED_LOG.exists():
        print(f"No seed log found, starting with seed {SEED_BASE}.")
        seed = SEED_BASE
    else:
        with PATH_SEED_LOG.open('r') as f:
            data = json.load(f)
            seed = data['seed'] + 1
            
    # Update the seed log file with the new seed and timestamp
    seed_log = {
        'seed': seed,
        'seed_time': str(datetime.now())
    }
    
    with PATH_SEED_LOG.open('w') as f:
        json.dump(seed_log, f, indent=4)

    return seed

def make_decks(seed: int, n_decks: int) -> np.ndarray:
    """
    Generates valid decks of cards. Each deck contains exactly 26 zeros (e.g., Black) 
    and 26 ones (e.g., Red).
    """
    rng = np.random.default_rng(seed)
    
    # Create a single base deck with 26 zeros and 26 ones
    base_deck = np.array([0] * CARDS_PER_COLOR + [1] * CARDS_PER_COLOR)
    
    # Duplicate the base deck for the requested number of decks
    decks = np.tile(base_deck, (n_decks, 1))
    
    # Shuffle the cards within each deck (row) independently
    rng.permuted(decks, axis=1, out=decks)
    
    return decks

def save_decks_npy(decks: np.ndarray, seed: int) -> Path:
    """
    Saves the 2D array of decks directly to a binary NumPy (.npy) file.
    """
    PATH_DECKS.mkdir(parents=True, exist_ok=True)
    n_decks, n_cards = decks.shape
    filename = PATH_DECKS / f'decks_{n_decks}x{n_cards}_seed{seed}.npy'
    
    print(f"Saving {n_decks:,} decks to {filename}...")
    np.save(filename, decks)
    print("Save complete!")
    
    return filename

if __name__ == "__main__":
    current_seed = get_next_seed()
    simulated_decks = make_decks(seed=current_seed, n_decks=5)
    save_decks_npy(decks=simulated_decks, seed=current_seed)