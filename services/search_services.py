from dataclasses import asdict

from clients.tmdb_client import TMDBClient
from services.cache_services import add_to_cache, get_from_cache
from services.normalize_services import normalize_movie_data


class SearchService:
    def __init__(self):
        self.tmdb_client = TMDBClient()

    def search_many(self, title):
        return self.tmdb_client.search_many(title)

    def search_movie(self, movie_id):
        cache_key = f"tmdb_movie_{movie_id}"
        cached_movie = get_from_cache(cache_key)

        if cached_movie:
            return cached_movie

        tmdb_data = self.tmdb_client.get_movie_details(movie_id)
        poster_url = self.tmdb_client.build_poster_url(tmdb_data.get("poster_path"))
        trailer_data = self.tmdb_client.get_trailer_data(tmdb_data)

        movie = normalize_movie_data(tmdb_data, trailer_data, poster_url)
        movie_dict = asdict(movie)

        add_to_cache(cache_key, movie_dict)
        return movie_dict

    def search_tv(self, tv_id):
        cache_key = f"tmdb_tv_{tv_id}"
        cached_tv = get_from_cache(cache_key)

        if cached_tv:
            return cached_tv

        tmdb_data = self.tmdb_client.get_tv_details(tv_id)
        poster_url = self.tmdb_client.build_poster_url(tmdb_data.get("poster_path"))
        trailer_data = self.tmdb_client.get_trailer_data(tmdb_data)

        tv_show = normalize_movie_data(tmdb_data, trailer_data, poster_url)
        tv_dict = asdict(tv_show)

        add_to_cache(cache_key, tv_dict)
        return tv_dict

    def get_movie_recommendations(self, movie_id):
        tmdb_data = self.tmdb_client.get_movie_details(movie_id)
        return self.tmdb_client.get_recommendations(tmdb_data)

    def get_tv_recommendations(self, tv_id):
        tmdb_data = self.tmdb_client.get_tv_details(tv_id)
        return self.tmdb_client.get_recommendations(tmdb_data)

    def get_movie_watch_providers(self, movie_id):
        cache_key = f"tmdb_movie_providers_{movie_id}"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        data = self.tmdb_client.get_movie_watch_providers(movie_id)
        add_to_cache(cache_key, data)
        return data

    def get_tv_watch_providers(self, tv_id):
        cache_key = f"tmdb_tv_providers_{tv_id}"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        data = self.tmdb_client.get_tv_watch_providers(tv_id)
        add_to_cache(cache_key, data)
        return data

    def get_popular_movies(self):
        return self.tmdb_client.get_popular_movies()

    def get_popular_tv(self):
        return self.tmdb_client.get_popular_tv()

    def get_mixed_popular(self):
        return self.tmdb_client.get_mixed_popular()

    def get_tv_season_details(self, tv_id, season_number):
        cache_key = f"tmdb_tv_season_{tv_id}_{season_number}"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        data = self.tmdb_client.get_tv_season_details(tv_id, season_number)
        add_to_cache(cache_key, data)
        return data

    def get_now_playing_movies(self):
        return self.tmdb_client.get_now_playing_movies()

    def get_top_rated_movies(self):
        return self.tmdb_client.get_top_rated_movies()

    def get_featured_content(self):
        return self.tmdb_client.get_featured_content()