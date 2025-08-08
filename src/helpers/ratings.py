####################################################################
#                                                                  #
#                   Copyright 2025 Caleb Schilly                   #
# See the LICENSE file at the top-level directory of this project. #
#                                                                  #
####################################################################

"""
Functions related to scraping a user's Letterboxd account
and prompting the user for manual ratings to all Nolan films.

Data used to predict user's personal rating of The Odyssey.
"""

import time

import requests
import numpy as np
from bs4 import BeautifulSoup

from src.helpers.utils import unformatTitle, formatTitle
from src.constants.films import ALL_FILMS

def starsToFloat(star_string):
    """Convert raw Letterboxd rating into float."""
    full_stars = star_string.count('★')
    half_star = '½' in star_string
    return full_stars + 0.5 * half_star

def printStatus(page: int):
    """Periodic prints while scraping Letterboxd data."""
    # TODO: Add a bunch more, and randomize the order
    statements = {
        1:  "Working through your logged films...",
        4:  "  Wading in deeper...",
        7:  "  Somebody's a cinephile...",
        10: "  This might take some time...",
        13: "  Feel free to throw on the Brutalist..."
    }
    if page in statements:
        print(statements[page])

def printFinished(page: int):
    """Output completion status."""
    print()
    if page < 4:
        print(f"Done! (Only {page} pages? Those are rookie numbers.)")
    elif page < 10:
        print("Done!")
    else:
        print(f"Done! (After {page} pages of entries??)")

def printStatistics(all_ratings: dict):
    """Show user how many films were found (and avg rating)."""
    n_ratings = len(all_ratings)
    print(f"  Looks like you've logged {n_ratings} Christopher Nolan films.")
    if n_ratings == 0:
        print("  Everybody starts somewhere.")
        return
    avg_rating = np.mean(list(all_ratings.values()))
    tag = ""
    if avg_rating < 2.0:
        tag = "I don't think we need Tiresias for this one..."
    elif avg_rating < 4.0:
        tag = "You're in luck: Tiresias does his best work on undecided minds."
    elif avg_rating < 5.0:
        tag = "Safe to say you'll probably like this one."
    elif avg_rating == 5.0:
        tag = "I say this with love: stop lying to yourself."
    print(f"  Your average rating across them all is {avg_rating}/5. {tag}")

def getLetterboxdRatings(error_counter = 0):
    """
    Query a user's Letterboxd for ratings of all available
    Nolan films.
    """
    lbxd_ratings = {}

    username = input(
        "Enter your Letterboxd username (or hit Enter to rate the films manually): "
    ).strip()
    if username == "":
        return lbxd_ratings

    base_url = f"https://letterboxd.com/{username}/films/ratings"
    page = 1

    while True:
        printStatus(page)
        url = f"{base_url}/page/{page}/"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            if page == 1 and error_counter < 3:
                print("Hm, there was an error loading your account. Let's try again.")
                ratings = getLetterboxdRatings(error_counter + 1)
                return ratings
            if error_counter >= 3:
                print("Let's just fill in your ratings manually.")
                return lbxd_ratings
            printFinished(page)
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        film_list = soup.find_all('li', class_='poster-container')

        if not film_list:
            break

        for film in film_list:
            film_title = unformatTitle(film.find('img')['alt'])
            rating_tag = film.find('span', class_='rating')

            if film_title in ALL_FILMS and rating_tag:
                rating = starsToFloat(rating_tag.text.strip())
                lbxd_ratings[film_title] = rating

        page += 1
        time.sleep(1)

    printStatistics(lbxd_ratings)
    print()

    return lbxd_ratings

def getManualRatingForFilm(film: str) -> float:
    """
    Prompt the user to manually rate the specified film.
    """
    while True:
        rating_input = input(f"  {formatTitle(film)}: ").strip().lower()
        if rating_input in ['s', 'skip']:
            return None
        try:
            rating = float(rating_input)
            if 0.0 <= rating <= 5.0:
                return rating
            print("  Please enter a number between 0 and 5 (decimals are ok!).")
        except ValueError:
            print("  Please enter a number between 0 and 5, or 's' to skip.")

def getAllManualRatings(ratings):
    """
    Prompt the user to manually rate every Nolan film.
    """
    print("For each film, enter a number between 0 and 5 (decimals are okay!).")
    print("(You can also enter 's' or 'skip' to move on to the next film.)")
    print()
    for film in ALL_FILMS:
        if film not in ratings:
            rating = getManualRatingForFilm(film)
            ratings[film] = rating
    return ratings

def getUserRatings(threshold=6) -> None:
    """
    Use getUserRatings() to
        1) query a user's Letterboxd account, and
        2) get the user's manual rating for any missing films.

    Returns a dictionary of ratings like:
        {
        <film1>: <rating1>,
        <film2>: <rating2>
        }
    """
    user_ratings = getLetterboxdRatings()
    print()
    if len(user_ratings) < threshold:
        run_manual = True
        run_manual_input = input(
            "Do you want to manually rate some more Nolan films "
            "to tune the model better? ([y], n): "
        ).lower().strip()
        while True:
            if run_manual_input in ["", "y", "yes"]:
                break
            if run_manual_input in ["n", "no"]:
                run_manual = False
                break
            run_manual_input = input(
                f"Sorry, I didn't recognize that input ({run_manual_input}). "
                "Please enter y or n."
            )

    if run_manual:
        user_ratings = getAllManualRatings(user_ratings)
        print()

    return user_ratings
