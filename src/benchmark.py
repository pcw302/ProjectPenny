import time
import numpy as np
from src.data_generation import get_next_seed, make_decks, save_decks_npy

def run_benchmark():
    n_decks = 10_000_000
    
    print(f"--- Starting Benchmark: {n_decks:,} Decks (.npy format) ---")
    start_total = time.perf_counter()
    
    seed = get_next_seed()
    
    # 1. Deck Generation
    t0 = time.perf_counter()
    decks = make_decks(seed=seed, n_decks=n_decks)
    t1 = time.perf_counter()
    print(f"Deck Generation Time: {t1 - t0:.2f} seconds")
    
    # 2. Disk Serialization (.npy)
    t2 = time.perf_counter()
    filepath = save_decks_npy(decks=decks, seed=seed)
    t3 = time.perf_counter()
    print(f"File Saving Time:     {t3 - t2:.2f} seconds")
    
    # 3. Read Speed Test
    t4 = time.perf_counter()
    loaded_decks = np.load(filepath)
    t5 = time.perf_counter()
    print(f"File Loading Time:    {t5 - t4:.2f} seconds")
    
    total_time = time.perf_counter() - start_total
    file_size_mb = filepath.stat().st_size / (1024 * 1024)
    
    print("----------------------------------------")
    print(f"Total Disk Space:     {file_size_mb:.2f} MB")
    print(f"Total Execution Time: {total_time:.2f} seconds")

if __name__ == "__main__":
    run_benchmark()