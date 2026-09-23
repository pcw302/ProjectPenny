import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_generation import get_next_seed, make_decks, save_decks_npy
from src.data_processing_bitwise import process_all_decks
from src.visualization import plot_heatmaps

def display_menu() -> None:
    """Displays available menu choices to the user."""
    print("\nHumble-Nishiyama Randomness Game")
    print("--------------------------------")
    print("1. Display current heatmaps")
    print("2. Simulate additional decks")
    print("3. Exit")

def handle_simulation() -> None:
    """Prompt user for deck count, generate, and process decks with bitwise engine."""
    user_input = input("Enter number of decks to simulate (e.g. 1000): ").strip()
    if not user_input.isdigit() or int(user_input) <= 0:
        print("Invalid deck count. Please enter a positive integer.")
        return

    num_decks = int(user_input)
    print(f"\n[1/2] Generating {num_decks:,} decks...")
    seed = get_next_seed()
    decks = make_decks(seed=seed, n_decks=num_decks)
    filepath = save_decks_npy(decks=decks, seed=seed)

    print(f"[2/2] Processing decks using bitwise engine...")
    total_processed = process_all_decks()
    print(f"Success! Total accumulated decks in database: {total_processed:,}")

def main() -> None:
    """Runs the interactive command-line interface."""
    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            plot_heatmaps()
        elif choice == "2":
            handle_simulation()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()