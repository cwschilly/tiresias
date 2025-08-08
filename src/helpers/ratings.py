import time

import requests
import numpy as np
from bs4 import BeautifulSoup

from src.helpers.utils import unformatTitle, formatTitle
from src.constants.films import ALL_FILMS

"""User ratings of Christopher Nolan films"""

def starsToFloat(star_string):
    full_stars = star_string.count('★')
    half_star = '½' in star_string
    return full_stars + 0.5 * half_star

def printStatus(page: int):
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
    print()
    if page < 4:
        print(f"Done! (Only {page} pages? Those are rookie numbers.)")
    elif page < 10:
        print(f"Done!")
    else:
        print(f"Done! (After {page} pages of entries??)")

def printStatistics(all_ratings: dict):
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
    lbxd_ratings = {}

    username = input("Enter your Letterboxd username (or just hit Enter to rate the films manually): ").strip()
    if username == "":
        return lbxd_ratings

    base_url = f"https://letterboxd.com/{username}/films/ratings"
    page = 1

    while True:
        printStatus(page)
        url = f"{base_url}/page/{page}/"
        response = requests.get(url)
        if response.status_code != 200:
            if page == 1 and error_counter < 3:
                print("Hm, there was an error loading your account. Let's try again.")
                ratings = getLetterboxdRatings(error_counter + 1)
                return ratings
            elif error_counter >= 3:
                print("Let's just fill in your ratings manually.")
                return lbxd_ratings
            else:
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
    while True:
        rating_input = input(f"  {formatTitle(film)}: ").strip().lower()
        if rating_input in ['s', 'skip']:
            return None
        try:
            rating = float(rating_input)
            if 0.0 <= rating <= 5.0:
                return rating
            else:
                print("  Please enter a number between 0 and 5 (decimals are ok!).")
        except ValueError:
            print("  Please enter a number between 0 and 5, or 's' to skip.")

def getAllManualRatings(ratings):
    print("For each film, enter a number between 0 and 5 (decimals are okay!).")
    print("(You can also enter 's' or 'skip' to move on to the next film.)")
    print()
    for film in ALL_FILMS:
        if film not in ratings:
            rating = getManualRatingForFilm(film)
            ratings[film] = rating
    return ratings

def getUserRatings(threshold=6) -> None:
    user_ratings = getLetterboxdRatings()
    print()
    if len(user_ratings) < threshold:
        run_manual = True
        run_manual_input = input(f"Do you want to manually rate some more Nolan films to tune the model better? ([y], n): ").lower().strip()
        while True:
            if run_manual_input in ["", "y", "yes"]:
                break
            elif run_manual_input in ["n", "no"]:
                run_manual = False
                break
            run_manual_input = input(f"Sorry, I didn't recognize that input ({run_manual_input}). Please enter y or n.")

    if run_manual:
        user_ratings = getAllManualRatings(user_ratings)
        print()

    return user_ratings