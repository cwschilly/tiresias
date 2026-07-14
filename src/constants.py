import os

## Filepaths
PROJECT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR      = os.path.join(PROJECT_DIR, "data")
DATA_FILEPATH = os.path.join(DATA_DIR, "responses.csv")
OUTPUT_DIR    = os.path.join(PROJECT_DIR, "output")
MODEL_DIR     = os.path.join(PROJECT_DIR, "model")

## The Nolan Index: (fabula craziness, syuzhet craziness), each 0-10
## Fabula  = how crazy the events are (dream heists, 5D bookshelves, bat-based vigilantism)
## Syuzhet = how crazy the telling is (nonlinearity, nested timelines, inversion)
## Yes, these are real narratology terms. This is a serious publication.
NOLAN_INDEX = {
    "following":             (3.0, 4.0),
    "memento":               (2.0, 8.0),
    "batman_begins":         (3.0, 1.0),
    "the_prestige":          (4.0, 7.0),
    "the_dark_knight":       (4.0, 1.0),
    "inception":             (5.0, 5.0),
    "the_dark_knight_rises": (3.0, 1.0),
    "interstellar":          (6.0, 2.0),
    "dunkirk":               (1.0, 7.0),
    "tenet":                 (10.0, 10.0),
    "oppenheimer":           (2.0, 4.0),
}

FILM_LABELS = {
    "following":             "Following (1998)",
    "memento":               "Memento (2000)",
    "batman_begins":         "Batman Begins (2005)",
    "the_prestige":          "The Prestige (2006)",
    "the_dark_knight":       "The Dark Knight (2008)",
    "inception":             "Inception (2010)",
    "the_dark_knight_rises": "The Dark Knight Rises (2012)",
    "interstellar":          "Interstellar (2014)",
    "dunkirk":               "Dunkirk (2017)",
    "tenet":                 "Tenet (2020)",
    "oppenheimer":           "Oppenheimer (2023)",
}

## Best guess for The Odyssey (2026); the website lets users drag this around
ODYSSEY_DEFAULT = {"label": "The Odyssey (2026)", "fabula": 3.0, "syuzhet": 6.0}

## Oscar record: (nominations, wins) per film — sources cited in README
OSCARS = {
    "following":             (0, 0),
    "memento":               (2, 0),
    "batman_begins":         (1, 0),
    "the_prestige":          (2, 0),
    "the_dark_knight":       (8, 2),
    "inception":             (8, 4),
    "the_dark_knight_rises": (0, 0),
    "interstellar":          (5, 1),
    "dunkirk":               (8, 3),
    "tenet":                 (2, 1),
    "oppenheimer":           (13, 7),
}

## Index coordinates are normalized to ~[0, 1] inside the affinity math
INDEX_SCALE = 10.0

## General
MIN_RATINGS = 3
ALL_FILMS   = list(NOLAN_INDEX.keys())
