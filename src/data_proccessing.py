# importing libraries
import numpy as np
import pandas as pd
from pathlib import Path


# file paths (may need to come back and correct later)
PATH_DECKS = Path("data/decks/")
PATH_PROCESSED = Path("data/processed/")
PATH_RESULTS = PATH_PROCESSED / "results.csv"


# all eight possible three-card patterns.
# 0 represents black and 1 represents red.
PATTERNS = [
    (0, 0, 0),  # BBB
    (0, 0, 1),  # BBR
    (0, 1, 0),  # BRB
    (0, 1, 1),  # BRR
    (1, 0, 0),  # RBB
    (1, 0, 1),  # RBR
    (1, 1, 0),  # RRB
    (1, 1, 1),  # RRR
]


def pattern_to_string(pattern: tuple) -> str:
    """Converting a numeric pattern such as (0, 1, 1) to 'BRR'."""

    letters = [] #creating empty list at first

    for card in pattern: # looping through to convert into string, 0 is black, 1 is red
        if card == 0:
            letters.append("B")
        else:
            letters.append("R")

    return "".join(letters) # producing letters 


def play_game(
    deck: list,
    my_choice: tuple,
    opponent_choice: tuple
) -> tuple:
    """
    Play one H-N game for one pair of player choices.

    Returns:
        my_tricks: Number of tricks won by player 1.
        opponent_tricks: Number of tricks won by opponent player.
        my_cards: Total number of cards won by player 1.
        opponent_cards: Total number of cards won by opponent player.
    """

    # initializing trick scores
    my_tricks = 0
    opponent_tricks = 0

    # initializing card scores 
    my_cards = 0
    opponent_cards = 0

    # creating the current pile 
    current_pile = []

    # going through the deck
    for card in deck:

        # adding the card to the pile
        current_pile.append(card)

        # checking pile length (if less than 3, continue)
        if len(current_pile) < 3:
            continue

        # getting the last three cards to check for comparison
        last_three = tuple(current_pile[-3:])

        # checking for a winner (my_choice matches the last 3 cards of the pile)
        if last_three == my_choice:

            # adding a score to my tricks (player 1 tricks)
            my_tricks += 1
            # for Ron's version (adding stack of cards to winner's pile)
            my_cards += len(current_pile)

            # clearing the pile 
            current_pile = []

        # same thing happening here, except we're checking for the opponent's choice
        elif last_three == opponent_choice:

            opponent_tricks += 1
            opponent_cards += len(current_pile)

            current_pile = []

    # returning 4 values as a final result(my tricks and cards, opponent's tricks and cards)
    return (
        my_tricks,
        opponent_tricks,
        my_cards,
        opponent_cards,
    )


def create_empty_results() -> dict:
    """Create counters for all 56 valid player matchups."""
    # this is how we're going to get our results from all the simulations! 

    # creating an empty dictionary
    results = {}

    # first loop: going through all 8 of my (player 1) possible choices
    for my_choice in PATTERNS:
        # second loop: doing same thing except for the opponent
        for opponent_choice in PATTERNS:

            # checking of players picked the same pattern (won't work! will skip over)
            if my_choice == opponent_choice:
                continue

            # creating match ups
            matchup = (my_choice, opponent_choice)

            # creating our counters
            results[matchup] = {
                "decks": 0,
                "hn_wins": 0,
                "hn_losses": 0,
                "hn_ties": 0,
                "ron_wins": 0,
                "ron_losses": 0,
                "ron_ties": 0,
            }

    # sending back the completed dictionary 
    return results


def process_deck(deck: list, results: dict) -> None:
    """Evaluate one deck for all 56 valid player matchups."""
    # function that receives the decks (one deck at a time)

    # looping through the choices again
    for my_choice in PATTERNS:
        for opponent_choice in PATTERNS:

            # skipping the same choices
            if my_choice == opponent_choice:
                continue

            # identifying the matchups we're currently looking at 
            matchup = (my_choice, opponent_choice)

            # basically playing the game and returning the results that we need from it
            (
                my_tricks,
                opponent_tricks,
                my_cards,
                opponent_cards,
            ) = play_game(
                deck,
                my_choice,
                opponent_choice,
            )

            # increasing deck counter (if the combo has already been tested on other decks)
            results[matchup]["decks"] += 1

            # scoring based on the original H-N game
            # comparing tricks and increasing count when true
            if my_tricks > opponent_tricks:
                results[matchup]["hn_wins"] += 1 

            elif my_tricks < opponent_tricks:
                results[matchup]["hn_losses"] += 1

            else:
                results[matchup]["hn_ties"] += 1

            # Score Ron's variation
            # comparing total cards won instead of tricks
            if my_cards > opponent_cards:
                results[matchup]["ron_wins"] += 1

            elif my_cards < opponent_cards:
                results[matchup]["ron_losses"] += 1

            else:
                results[matchup]["ron_ties"] += 1


def process_file(filepath: Path, results: dict) -> None:
    """Read a JSONL deck file and process every deck in it."""
    # trying to handle all of the simualtions...

    # just an f-string telling us it's processing (may need to check filepath)
    print(f"Processing {filepath}...")

    # reading in the json file
    dataframe = pd.read_json(
        filepath,
        lines=True,
    )

    # looping over the decks using the deck column, one at a time
    for deck in dataframe["deck"]:
        process_deck(deck, results)

    print("Processing complete!")



def results_to_dataframe(results: dict) -> pd.DataFrame:
    """Convert the results dictionary into a DataFrame."""
    # once all data is processed, going to convert to dataframe

    # creating an empty list for the rows
    rows = []

    # retrieving both key and value from dictionary (match up and scores)
    for matchup, scores in results.items():

        # unpacking the matchup 
        my_choice, opponent_choice = matchup

        # building one row 
        # creating a dictionary representing one row of our CSV 
        row = {
            "my_choice": pattern_to_string(my_choice), # converting numbers to letters
            "opponent_choice": pattern_to_string(opponent_choice), # same thing
            "decks": scores["decks"], # getting the number of decks tested
            # copying over results
            "hn_wins": scores["hn_wins"],
            "hn_losses": scores["hn_losses"],
            "hn_ties": scores["hn_ties"],
            "ron_wins": scores["ron_wins"],
            "ron_losses": scores["ron_losses"],
            "ron_ties": scores["ron_ties"],
        }

        # adding the row to the list
        rows.append(row)

    # converting all of the rows into a table
    return pd.DataFrame(rows)


def save_results(results: dict) -> None:
    """Save processed game results as a CSV file."""

    # creating the path if it doesn't yet exist
    PATH_PROCESSED.mkdir(
        parents=True,
        exist_ok=True,
    )

    # converting the dictionary into a table 
    dataframe = results_to_dataframe(results)

    # now saving that table as a csv
    dataframe.to_csv(
        PATH_RESULTS,
        index=False,
    )

    # just telling us where the file was saved
    print(f"Results saved to {PATH_RESULTS}")


if __name__ == "__main__":

    results = create_empty_results()

    deck_files = sorted(PATH_DECKS.glob("*.jsonl"))

    for filepath in deck_files:
        process_file(filepath, results)

    save_results(results)