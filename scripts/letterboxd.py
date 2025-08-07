import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

from constants.films import ALL_FILMS
from helpers.utils import format_list_of_films

"""Work-in-progress; script to query a user's Letterboxd account to get personal Nolan ratings."""

def stars_to_float(star_string):
    full_stars = star_string.count('★')
    half_star = '½' in star_string
    return full_stars + 0.5 * half_star

def print_status(page: int):
    statements = {
        1: "Working through your logged films...",
        4: "Wading in deeper...",
        7: "Somebody's a cinephile...",
        10: "This might take some time...",
        13: "Feel free to throw on the Brutalist..."
    }
    if page in statements:
        print(statements[page])

def print_complete(page: int):
    if page < 4:
        print(f"Done! (Only {page} pages? You gotta get those numbers up.)")
    elif page < 10:
        print(f"Done!")
    else:
        print(f"Done! ({page} pages of entries??)")

def get_letterboxd_ratings(username):
    base_url = f"https://letterboxd.com/{username}/films/ratings/"
    page = 1
    all_ratings = {}

    while True:
        print_status(page)
        url = f"{base_url}page/{page}/"
        response = requests.get(url)
        if response.status_code != 200:
            print_complete(page)
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        film_list = soup.find_all('li', class_='poster-container')

        if not film_list:
            break

        for film in film_list:
            film_title = film.find('img')['alt']
            rating_tag = film.find('span', class_='rating')

            if film_title in format_list_of_films(ALL_FILMS.keys()) and rating_tag:
                rating = stars_to_float(rating_tag.text.strip())
                all_ratings[film_title] = rating

        page += 1
        time.sleep(1)

    df = pd.DataFrame([
        {'title': title, 'rating': all_ratings.get(title, None)}
        for title in format_list_of_films(ALL_FILMS.keys())
    ])

    return df

def main():
    username = input("Enter your Letterboxd username: ")
    df = get_letterboxd_ratings(username)
    print("\nNolan Film Ratings:")
    print(df)

if __name__ == "__main__":
    main()
