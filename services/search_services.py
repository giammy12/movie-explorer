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

    # =========================
    # GENERI FILM / SERIE
    # =========================

    def get_movie_genres(self):
        cache_key = "tmdb_movie_genres"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        genres = self.tmdb_client.get_movie_genres()
        add_to_cache(cache_key, genres)
        return genres

    def get_tv_genres(self):
        cache_key = "tmdb_tv_genres"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        genres = self.tmdb_client.get_tv_genres()
        add_to_cache(cache_key, genres)
        return genres

    # =========================
    # CATALOGO FILM PER GENERE
    # =========================

    def get_movies_grouped_by_genre(self, max_genres=6, items_per_genre=24):
        cache_key = f"catalog_movies_grouped_{max_genres}_{items_per_genre}"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        genres = self.get_movie_genres()
        grouped = []

        for genre in genres[:max_genres]:
            genre_id = genre.get("id")
            genre_name = genre.get("name", "Genere")

            items = self.tmdb_client.get_movies_for_genre_blocks(
                genre_id,
                total_items=items_per_genre
            )

            normalized_items = []
            seen_ids = set()

            for item in items:
                item_id = item.get("id")
                if not item_id or item_id in seen_ids:
                    continue

                seen_ids.add(item_id)

                normalized_items.append({
                    "id": item_id,
                    "title": item.get("title", ""),
                    "poster_path": item.get("poster_path"),
                    "backdrop_path": item.get("backdrop_path"),
                    "overview": item.get("overview", ""),
                    "release_date": item.get("release_date", ""),
                    "vote_average": item.get("vote_average", 0),
                    "media_type": "movie"
                })

            grouped.append({
                "genre_id": genre_id,
                "genre_name": genre_name,
                "row_1": normalized_items[:12],
                "row_2": normalized_items[12:24]
            })

        add_to_cache(cache_key, grouped)
        return grouped

    # =========================
    # CATALOGO SERIE TV PER GENERE
    # =========================

    def get_tv_grouped_by_genre(self, max_genres=6, items_per_genre=24):
        cache_key = f"catalog_tv_grouped_{max_genres}_{items_per_genre}"
        cached = get_from_cache(cache_key)

        if cached:
            return cached

        genres = self.get_tv_genres()
        grouped = []

        for genre in genres[:max_genres]:
            genre_id = genre.get("id")
            genre_name = genre.get("name", "Genere")

            items = self.tmdb_client.get_tv_for_genre_blocks(
                genre_id,
                total_items=items_per_genre
            )

            normalized_items = []
            seen_ids = set()

            for item in items:
                item_id = item.get("id")
                if not item_id or item_id in seen_ids:
                    continue

                seen_ids.add(item_id)

                normalized_items.append({
                    "id": item_id,
                    "name": item.get("name", ""),
                    "poster_path": item.get("poster_path"),
                    "backdrop_path": item.get("backdrop_path"),
                    "overview": item.get("overview", ""),
                    "first_air_date": item.get("first_air_date", ""),
                    "vote_average": item.get("vote_average", 0),
                    "media_type": "tv"
                })

            grouped.append({
                "genre_id": genre_id,
                "genre_name": genre_name,
                "row_1": normalized_items[:12],
                "row_2": normalized_items[12:24]
            })

        add_to_cache(cache_key, grouped)
        return grouped
    

    def get_movie_detail(self, movie_id: int):
        data = self.tmdb_client.get_movie_details(movie_id)
        if not data:
            return None
        return self._serialize_movie_detail(data)


    def get_tv_detail(self, tv_id: int):
        data = self.tmdb_client.get_tv_details(tv_id)
        if not data:
            return None
        return self._serialize_tv_detail(data)
    

    def get_tv_season_detail(self, tv_id: int, season_number: int):
        data = self.tmdb_client.get_tv_season_details(tv_id, season_number)
        if not data:
            return None
        return data


    def _serialize_movie_detail(self, data: dict):
        return {
            "id": data.get("id"),
            "title": data.get("title", ""),
            "overview": data.get("overview", ""),
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "vote_average": data.get("vote_average", 0.0),
            "runtime": data.get("runtime"),
            "release_date": data.get("release_date"),
            "genres": data.get("genres", []),
            "credits": {
                "cast": [
                    {
                        "id": c.get("id"),
                        "name": c.get("name", ""),
                        "character": c.get("character"),
                        "profile_path": c.get("profile_path")
                    }
                    for c in data.get("credits", {}).get("cast", [])[:10]
                ]
            },
            "videos": {
                "results": [
                    {
                        "key": v.get("key"),
                        "name": v.get("name", ""),
                        "site": v.get("site", ""),
                        "type": v.get("type", "")
                    }
                    for v in data.get("videos", {}).get("results", [])
                ]
            },
            "watchProviders": {
                "results": data.get("watch/providers", {}).get("results", {})
            }
        }
    

    def _serialize_tv_detail(self, data: dict):
        return {
            "id": data.get("id"),
            "name": data.get("name", ""),
            "overview": data.get("overview", ""),
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "vote_average": data.get("vote_average", 0.0),
            "episode_run_time": data.get("episode_run_time", []),
            "first_air_date": data.get("first_air_date"),
            "genres": data.get("genres", []),
            "number_of_seasons": data.get("number_of_seasons", 0),
            "number_of_episodes": data.get("number_of_episodes", 0),
            "seasons": [
                {
                    "id": s.get("id"),
                    "season_number": s.get("season_number"),
                    "name": s.get("name", ""),
                    "episode_count": s.get("episode_count", 0),
                    "poster_path": s.get("poster_path")
                }
                for s in data.get("seasons", [])
            ],
            "credits": {
                "cast": [
                    {
                        "id": c.get("id"),
                        "name": c.get("name", ""),
                        "character": c.get("character"),
                        "profile_path": c.get("profile_path")
                    }
                    for c in data.get("credits", {}).get("cast", [])[:10]
                ]
            },
            "videos": {
                "results": [
                    {
                        "key": v.get("key"),
                        "name": v.get("name", ""),
                        "site": v.get("site", ""),
                        "type": v.get("type", "")
                    }
                    for v in data.get("videos", {}).get("results", [])
                ]
            },
            "watchProviders": {
                "results": data.get("watch/providers", {}).get("results", {})
            }
        }