# ProjectPenny

**Data 440: Automation and Workflows**

The program uses 3 modules to produce the final data. This document details the first module: **`DataGeneration.py`**.

---

## The Game

This repository simulates and visualizes two versions of the Humble-Nishiyama (H-N) Randomness Game which is a variation of the Penney's Game. 

### Penney's Game

The Penney Game is a game based on flipping a coin multiple times. Each player chooses a pattern for 3 observations (Head, Head, Head | Tail, Tail, Tail | Heat, Tail, Head, etc.), and the player that has the most observed pattern of coin flips wins. However there is a way to win this game. Let Player 1 choose a pattern (1, 2, 3), and then based off that pattern, player 2 will select their pattern using this formula: (not 2(opposite of second choice), 1, 2). Using Heads and Tails, it would look something like this: P1: H T H | P2: H H T. 

### Humble Nishiyama Randomness Game 

### Version 1 

Version 1 is based on tricks, where the winning player receives a point for winning the pile.

### Version 2 

Version 2 is based on cards, where the win is determined by the amount of cards each player has at the end of the deck.

## Purpose of Investigation 

The main purpose of our investigation is to compare the strategies and winning probabilities of the two version 

## How to Run our Code

By running our main.py file from the command line in the of the project you will be given 4 options;
First is to run the entire pipeline, creating new decks, processing them and then putting the results into a heat map returned at the end of the function call.
Option 2 is to recalculate the winning percentages for all existing decks from scratch, mainly for debugging 
Option 3 is to just return the existing heat map
Option 4 is to exit

## Data Module: DataGeneration.py

This module creates the "decks" and writes them to a numpy binary file.

### How It Works

* **Seed Management**: Reads the last used seed from a central JSON file called `seed.json` and increments it by 1 for the current iteration. If no log exists, it creates `seed.json` and starts at seed `1`.
* **Deck Creation**: `make_decks` takes a `seed` and `n_decks` and creates a base deck of 26 `0`s (Black) and 26 `1`s (Red).
* **Matrix Scaling (`np.tile`)**: To make decks at scale, `np.tile` creates a 2D matrix with `n_decks` rows $\times$ 52 columns. This is much faster than using a `for` loop and enables the next vectorized shuffling step.
* **Independent Shuffling (`rng.permuted`)**: The 2D matrix is passed through NumPy's random module:
`rng.permuted(decks, axis=1, out=decks)`
* `axis=1` tells the function to shuffle across the columns, meaning every row is shuffled independently of the others. Cards stay in their own row, but their order is randomized. Basically, if we put a single `2` in every deck in the same position, after the function call there would still only be a single `2` in each row, but in random positions.
* `out=decks` performs the operation in-place, which prevents having to make a copy of the matrix in memory.



### File Storage (`numpy binary`)
The decks are saved as numpy binary files allowing streaming of data into memory as bits instead of having to load the entire file at once.

1. **Directory Setup**: Ensures the correct directory structure exists; if not, it creates it.
2. **Dimension Extraction**: Gets the shape of the matrix with `decks.shape` to extract `n_decks` and `n_cards`. The card count defaults to 52, but it is not hardcoded in case project requirements change later.
3. **Dynamic Filenames**: Embeds the matrix dimensions directly into the filename to make troubleshooting easy.
4. **Numpy Binary**: Saves the matrix using the np.save function and chunks them based on the file size, anything larger then 45MB being split into a different file.


## Data Module: data_processing_bitwise.py
Cards are represented as binary values, either 0 or one corresponding to black or read, this allows each possible pattern to be encoded as a 3 bit integer 0-7. 
We stream in the decks which are saved as numpy binary files, we then take each deck and calculate all the possible 3 bit windows in that deck, which are turned into integer values (0-7) and stored in an array
We then loop through the array of values and check to see which corresponds with the selected patterns and score accordingly. These values are then written into a results_bitwise.csv file to be read by the visualization module.
We also only load and calculate the results for the newly generated decks, to improve efficiency.


## Data Module: visualization.py 
Read out of the results_bitwise.csv to get data on wins and losses
Once read into a pandas data frame, various dataframe operations are performed in order to get the data in the right format to be read by seaborn then output by matplotlib
The most recent heatmap is saved to the figures directory and is over-written when a new plot is generated.

## Findings
The biggest finding from our results is that the game is heavily skewed towards player 2, infact in both variations, it is nearly statistically impossible for player 1 to win if player 2 chooses the correct pattern.
If your opponent chooses X1 X2 X3 , you can nearly guarantee a win or tie by choosing Not X2, X1, X2. Also in Rons variation becuase your are scoring by cards instead of tricks, ties are much less likely. 
