import sys
from pathlib import Path

from src.data_generation import get_next_seed, make_decks, save_decks_npy
from src.data_processing_bitwise import process_new_decks, process_all_decks
from src.visualization import plot_heatmaps


def run_pipeline(n_decks: int = 100_000) -> None:
    """
    Executes the Penney's Game pipeline:
    1. Generates and saves new decks (chunked at 45 MB).
    2. Incrementally processes ONLY the newly saved deck file(s).
    3. Renders, saves to figures/, and displays side-by-side heatmaps.
    """
    print("\n==============================================")
    print("   PENNEY'S GAME AUTOMATED PIPELINE RUNNER    ")
    print("==============================================")

    # 1. Generate new decks
    print(f"\n[Step 1/3] Generating {n_decks:,} new decks...")
    seed = get_next_seed()
    decks = make_decks(seed=seed, n_decks=n_decks)
    saved_paths = save_decks_npy(decks=decks, seed=seed)

    # 2. Process ONLY the newly saved deck file(s)
    print("\n[Step 2/3] Incrementally processing new deck file(s)...")
    total_processed = process_new_decks(saved_paths)
    print(f"--> Done! Total accumulated decks in dataset: {total_processed:,}")

    # 3. Visualize & export heatmaps
    print("\n[Step 3/3] Generating and saving heatmaps to figures/...")
    plot_heatmaps()

    print("\n[Complete] Pipeline finished successfully!")


def main() -> None:
    """Interactive CLI menu for executing and testing project components."""
    while True:
        print("\n==============================================")
        print("          PENNEY'S GAME MAIN MENU             ")
        print("==============================================")
        print("1. Run Pipeline (Generate + Process New + Plot)")
        print("2. Reprocess ALL Existing Decks from Scratch")
        print("3. Plot Heatmaps Only (From existing CSV)")
        print("4. Exit")
        print("----------------------------------------------")

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            try:
                num_input = input("Enter number of new decks to generate [Default: 100,000]: ").strip()
                n_decks = int(num_input) if num_input else 100_000
                run_pipeline(n_decks=n_decks)
            except ValueError:
                print("\n[Error] Invalid integer entered. Please try again.")

        elif choice == "2":
            print("\nReprocessing all deck files in data/decks/...")
            total = process_all_decks()
            if total > 0:
                print(f"--> Done! Reprocessed {total:,} total decks.")
                plot_heatmaps()
            else:
                print("\n[Error] No deck files found in data/decks/. Run Option 1 first.")

        elif choice == "3":
            plot_heatmaps()

        elif choice == "4":
            print("\nExiting. Goodbye!")
            sys.exit(0)

        else:
            print("\n[Error] Invalid choice. Please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()