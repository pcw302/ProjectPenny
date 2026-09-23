def display_menu() -> None:
    """displaying the available options to the user"""

    print("\nHumble-Nishiyama Randomness Game")
    print("--------------------------------")
    print("1. Display current heatmaps")
    print("2. Simulate additional decks")
    print("3. Exit")


def main() -> None:
    """Running the command-line interface."""

    while True:
        display_menu()

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            print("Displaying heatmaps...")

        elif choice == "2":
            print("Adding simulations...")

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()