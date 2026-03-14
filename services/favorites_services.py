import json
import os

FAVORITES_FILE = "data/favorites.json"


def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []

    with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
        json.dump(favorites, file, indent=4)


def add_favorite(movie_dict):
    favorites = load_favorites()

    for favorite in favorites:
        if favorite["imdb_id"] == movie_dict["imdb_id"]:
            return

    favorites.append(movie_dict)
    save_favorites(favorites)


def list_favorites():
    return load_favorites()


def remove_favorite(imdb_id):
    favorites = load_favorites()

    updated_favorites = []

    for movie in favorites:
        if movie.get("imdb_id") != imdb_id:
            updated_favorites.append(movie)

    save_favorites(updated_favorites)