import os

## Filepaths
PROJECT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR      = os.path.join(PROJECT_DIR, "data")
DATA_FILEPATH = os.path.join(DATA_DIR, "responses.csv")
OUTPUT_DIR    = os.path.join(PROJECT_DIR, "output")

## Features: [wackiness, budget_m, runtime, is_original, star_power, is_rated_r]
FILM_FEATURES = {
    "following":              [0.2,  0.006, 70,  1, 10,  0],
    "memento":                [0.8,  0.009, 113, 1, 30,  1],
    "insomnia":               [0.1,  0.046, 118, 0, 60,  1],
    "batman_begins":          [0.1,  0.150, 140, 0, 85,  0],
    "the_prestige":           [0.6,  0.040, 130, 0, 90,  0],
    "the_dark_knight":        [0.2,  0.185, 152, 0, 95,  0],
    "inception":              [0.7,  0.160, 148, 1, 88,  0],
    "the_dark_knight_rises":  [0.1,  0.250, 164, 0, 90,  0],
    "interstellar":           [0.7,  0.165, 169, 1, 85,  0],
    "dunkirk":                [0.5,  0.100, 106, 0, 80,  0],
    "tenet":                  [2.1,  0.205, 150, 1, 80,  0],
    "oppenheimer":            [0.4,  0.100, 180, 0, 92,  0],
}

## General
N_COMPONENTS = 3
MIN_RATINGS  = 3

## Derived values
N_FILM_FEATURES = len(next(iter(FILM_FEATURES.values())))
ALL_FILMS = list(FILM_FEATURES.keys())
N_FILMS   = len(ALL_FILMS)
INPUT_DIM = N_COMPONENTS + N_FILM_FEATURES

## Training
NUM_EPOCHS = 200