import sys
from pathlib import Path

# Force Python to find the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from src.data_generation import make_decks
import src.data_processing as original_mod
import src.data_processing_bitwise as bitwise_mod

DECKS = 1000000

def run_comparison():
    print(f"Generating {DECKS:,} test decks for validation...")
    # Fixed argument names to match data_generation signature: seed and n_decks
    test_decks = make_decks(seed=42, n_decks=DECKS)

    # 1. Run Original Implementation (isolated in-memory)
    print("\n[1/2] Running Original (Tuple/List) Implementation...")
    orig_results = original_mod.init_results_dict()
    
    start_orig = time.perf_counter()
    for deck in test_decks:
        original_mod.process_deck(deck, orig_results)
    time_orig = time.perf_counter() - start_orig

    # 2. Run Bitwise Implementation (isolated in-memory)
    print("[2/2] Running Bitwise Implementation...")
    bit_results = bitwise_mod.init_results_dict()
    
    start_bit = time.perf_counter()
    for deck in test_decks:
        bitwise_mod.process_deck(deck, bit_results)
    time_bit = time.perf_counter() - start_bit

    # 3. Assert Equivalence Across All 56 Matchups
    print("\n--- Verifying ---")
    mismatches = 0
    
    for (p1_tuple, p2_tuple), orig_data in orig_results.items():
        p1_int = original_mod.PATTERNS.index(p1_tuple)
        p2_int = original_mod.PATTERNS.index(p2_tuple)
        
        bit_data = bit_results[(p1_int, p2_int)]
        
        for key in ["decks", "hn_wins", "hn_losses", "hn_ties", "ron_wins", "ron_losses", "ron_ties"]:
            if orig_data[key] != bit_data[key]:
                print(f"MISMATCH in matchup {p1_tuple} vs {p2_tuple} for key '{key}':")
                print(f"  Original: {orig_data[key]} | Bitwise: {bit_data[key]}")
                mismatches += 1

    if mismatches == 0:
        print("SUCCESS: Both implementations produced identical results")
    else:
        print(f"FAILURE: Found {mismatches} mismatch(es) between algorithms.")

    # 4. Benchmarks
    print(f"\n--- Execution Time Comparison ({DECKS:,} Decks / {DECKS // 5600:,} Matchups) ---")
    print(f"Original Time:  {time_orig:.4f} seconds")
    print(f"Bitwise Time:   {time_bit:.4f} seconds")
    speedup = ((time_orig - time_bit) / time_orig) * 100
    print(f"Speedup:        {speedup:.1f}% faster")

if __name__ == "__main__":
    run_comparison()