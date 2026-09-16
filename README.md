# ProjectPenny

**Data 440: Automation and Workflows**

The program uses 3 modules to produce the final data. This document details the first module: **`DataGeneration.py`**.

---

## Data Module: DataGeneration.py

This module creates the "decks" and writes them to a JSON Lines file.

### How It Works

* **Seed Management**: Reads the last used seed from a central JSON file called `seed.json` and increments it by 1 for the current iteration. If no log exists, it creates `seed.json` and starts at seed `1`.
* **Deck Creation**: `make_decks` takes a `seed` and `n_decks` and creates a base deck of 26 `0`s (Black) and 26 `1`s (Red).
* **Matrix Scaling (`np.tile`)**: To make decks at scale, `np.tile` creates a 2D matrix with `n_decks` rows $\times$ 52 columns. This is much faster than using a `for` loop and enables the next vectorized shuffling step.
* **Independent Shuffling (`rng.permuted`)**: The 2D matrix is passed through NumPy's random module:
`rng.permuted(decks, axis=1, out=decks)`
* `axis=1` tells the function to shuffle across the columns, meaning every row is shuffled independently of the others. Cards stay in their own row, but their order is randomized. Basically, if we put a single `2` in every deck in the same position, after the function call there would still only be a single `2` in each row, but in random positions.
* `out=decks` performs the operation in-place, which prevents having to make a copy of the matrix in memory.



### File Storage (`save_decks_jsonl`)

After evaluating the best compromise between storage efficiency and readability, JSON Lines (`.jsonl`) was selected to store the decks.

`save_decks_jsonl` takes in the 2D deck matrix and the `seed`:

1. **Directory Setup**: Ensures the correct directory structure exists; if not, it creates it.
2. **Dimension Extraction**: Gets the shape of the matrix with `decks.shape` to extract `n_decks` and `n_cards`. The card count defaults to 52, but it is not hardcoded in case project requirements change later.
3. **Dynamic Filenames**: Embeds the matrix dimensions directly into the filename to make troubleshooting easy.
4. **Data Transformation**: Converts the 2D NumPy array into a list of lists so that it can be read into a JSON format through Pandas.
5. **Pandas Optimization**: Uses Pandas to read/write JSON Lines instead of built-in Python libraries because Pandas is written in low-level C. This speeds up operations when processing millions of values.
6. **DataFrame Wrapping**: Converts the list of lists into a DataFrame where `"deck"` is the column name and each row contains the full deck array.
7. **JSON Lines Output**: Uses `df.to_json()` to convert the DataFrame into a `.jsonl` file while treating every entry as a key-value JSON object.