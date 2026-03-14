import json
import os

CACHE_FILE = "data/cache.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return{}
    
    with open(CACHE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    

def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache_data, file, indent=4)


def get_from_cache(title):
    cache = load_cache()
    normalized_title = title.strip().lower()
    
    return cache.get(normalized_title)


def add_to_cache(title, movie_dict):
    cache = load_cache()
    normalized_title = title.strip().lower()
    cache[normalized_title] = movie_dict
    save_cache(cache)





