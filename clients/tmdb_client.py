import time
import requests

from config import TMDB_API_KEY
from exceptions import APIError, InvalidResponseError, NotFoundError


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w342"
    HERO_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 1800  # 30 minuti

    def _cache_get(self, key):
        cached = self._cache.get(key)

        if not cached:
            return None

        value, timestamp = cached

        if time.time() - timestamp > self._cache_ttl:
            self._cache.pop(key, None)
            return None

        return value

    def _cache_set(self, key, value):
        self._cache[key] = (value, time.time())

    def _request(self, endpoint, params=None, error_message="Errore nella richiesta TMDb", use_cache=True):
        params = params or {}

        cache_key = f"{endpoint}|{tuple(sorted(params.items()))}"

        if use_cache:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

        url = f"{self.BASE_URL}{endpoint}"

        final_params = {
            "api_key": TMDB_API_KEY,
            **params
        }

        try:
            response = requests.get(url, params=final_params, timeout=10)
        except requests.RequestException as error:
            raise APIError(f"Errore di connessione a TMDb: {error}")

        if response.status_code == 404:
            raise NotFoundError("Contenuto non trovato")

        if response.status_code != 200:
            raise APIError(error_message)

        try:
            data = response.json()
        except ValueError:
            raise InvalidResponseError("La risposta di TMDb non è un JSON valido")

        if use_cache:
            self._cache_set(cache_key, data)

        return data

    def build_poster_url(self, poster_path):
        if not poster_path:
            return ""
        return f"{self.IMAGE_BASE_URL}{poster_path}"

    def build_hero_backdrop_url(self, backdrop_path):
        if not backdrop_path:
            return ""
        return f"{self.HERO_IMAGE_BASE_URL}{backdrop_path}"

    def search_many(self, query):
        data = self._request(
            "/search/multi",
            params={
                "query": query,
                "language": "it-IT",
                "region": "IT"
            },
            error_message="Errore nella richiesta TMDb",
            use_cache=False
        )

        results = data.get("results", [])

        filtered_results = [
            item for item in results
            if item.get("media_type") in ["movie", "tv"]
        ]

        if not filtered_results:
            raise NotFoundError("Nessun risultato trovato")

        return filtered_results

    def get_movie_details(self, movie_id):
        data = self._request(
            f"/movie/{movie_id}",
            params={
                "language": "it-IT",
                "append_to_response": "videos,credits,recommendations"
            },
            error_message="Errore nella richiesta dettagli film TMDb"
        )

        if "id" not in data:
            raise InvalidResponseError("Risposta dettagli film TMDb non valida")

        return data

    def get_tv_details(self, tv_id):
        data = self._request(
            f"/tv/{tv_id}",
            params={
                "language": "it-IT",
                "append_to_response": "videos,credits,recommendations"
            },
            error_message="Errore nella richiesta dettagli serie TMDb"
        )

        if "id" not in data:
            raise InvalidResponseError("Risposta dettagli serie TMDb non valida")

        return data

    def get_tv_season_details(self, tv_id, season_number):
        data = self._request(
            f"/tv/{tv_id}/season/{season_number}",
            params={
                "language": "it-IT"
            },
            error_message="Errore nella richiesta dettagli stagione TMDb"
        )

        if "episodes" not in data:
            raise InvalidResponseError("Risposta dettagli stagione TMDb non valida")

        return data

    def get_trailer_data(self, details_data):
        videos = details_data.get("videos", {}).get("results", [])

        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                video_key = video.get("key", "")
                return {
                    "title": video.get("name", ""),
                    "url": f"https://www.youtube.com/watch?v={video_key}",
                    "video_id": video_key
                }

        return None

    def get_recommendations(self, details_data):
        items = details_data.get("recommendations", {}).get("results", [])

        recommendations = []
        for item in items[:6]:
            recommendations.append({
                "id": item.get("id"),
                "title": item.get("title") or item.get("name", ""),
                "poster_url": self.build_poster_url(item.get("poster_path")),
                "year": (item.get("release_date") or item.get("first_air_date") or "")[:4],
                "media_type": item.get("media_type", "")
            })

        return recommendations

    def get_movie_watch_providers(self, movie_id):
        data = self._request(
            f"/movie/{movie_id}/watch/providers",
            error_message="Errore nella richiesta watch providers film TMDb"
        )

        return data.get("results", {}).get("IT", {})

    def get_tv_watch_providers(self, tv_id):
        data = self._request(
            f"/tv/{tv_id}/watch/providers",
            error_message="Errore nella richiesta watch providers serie TMDb"
        )

        return data.get("results", {}).get("IT", {})

    def get_now_playing_movies(self):
        data = self._request(
            "/movie/now_playing",
            params={
                "language": "it-IT",
                "region": "IT",
                "page": 1
            },
            error_message="Errore nella richiesta film in sala TMDb"
        )

        return data.get("results", [])[:12]

    def get_top_rated_movies(self):
        data = self._request(
            "/movie/top_rated",
            params={
                "language": "it-IT",
                "page": 1
            },
            error_message="Errore nella richiesta film top rated TMDb"
        )

        return data.get("results", [])[:12]

    def get_popular_movies(self):
        data = self._request(
            "/movie/popular",
            params={
                "language": "it-IT",
                "region": "IT",
                "page": 1
            },
            error_message="Errore nella richiesta film popolari TMDb"
        )

        return data.get("results", [])[:12]

    def get_popular_tv(self):
        data = self._request(
            "/tv/popular",
            params={
                "language": "it-IT",
                "page": 1
            },
            error_message="Errore nella richiesta serie popolari TMDb"
        )

        return data.get("results", [])[:12]

    def get_mixed_popular(self):
        movies = self.get_popular_movies()
        tv_shows = self.get_popular_tv()

        mixed_items = []

        for movie in movies:
            movie["media_type"] = "movie"
            mixed_items.append(movie)

        for tv in tv_shows:
            tv["media_type"] = "tv"
            mixed_items.append(tv)

        mixed_items.sort(key=lambda item: item.get("popularity", 0), reverse=True)

        return mixed_items[:20]

    def get_featured_content(self):
        now_playing = self.get_now_playing_movies()
        top_rated = self.get_top_rated_movies()
        popular = self.get_popular_movies()

        candidates = now_playing[:6] + top_rated[:4] + popular[:4]

        filtered = [
            item for item in candidates
            if item.get("backdrop_path") and item.get("overview")
        ]

        if not filtered:
            return []

        filtered.sort(
            key=lambda item: (
                item.get("vote_average", 0),
                item.get("popularity", 0)
            ),
            reverse=True
        )

        unique_items = []
        seen_ids = set()

        for item in filtered:
            if item["id"] not in seen_ids:
                item["media_type"] = "movie"
                unique_items.append(item)
                seen_ids.add(item["id"])

        return unique_items[:5]

    # =========================
    # GENERI
    # =========================

    def get_movie_genres(self):
        data = self._request(
            "/genre/movie/list",
            params={"language": "it-IT"},
            error_message="Errore nella richiesta generi film TMDb"
        )
        return data.get("genres", [])

    def get_tv_genres(self):
        data = self._request(
            "/genre/tv/list",
            params={"language": "it-IT"},
            error_message="Errore nella richiesta generi serie TV TMDb"
        )
        return data.get("genres", [])

    # =========================
    # DISCOVER PER GENERE
    # =========================

    def discover_movies_by_genre(self, genre_id, page=1):
        data = self._request(
            "/discover/movie",
            params={
                "language": "it-IT",
                "region": "IT",
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "include_video": "false",
                "with_genres": genre_id,
                "page": page
            },
            error_message="Errore nella richiesta film per genere TMDb"
        )

        return data.get("results", [])

    def discover_tv_by_genre(self, genre_id, page=1):
        data = self._request(
            "/discover/tv",
            params={
                "language": "it-IT",
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "with_genres": genre_id,
                "page": page
            },
            error_message="Errore nella richiesta serie TV per genere TMDb"
        )

        return data.get("results", [])

    def get_movies_for_genre_blocks(self, genre_id, total_items=24):
        items = []
        page = 1

        while len(items) < total_items and page <= 3:
            results = self.discover_movies_by_genre(genre_id, page=page)
            if not results:
                break
            items.extend(results)
            page += 1

        return items[:total_items]

    def get_tv_for_genre_blocks(self, genre_id, total_items=24):
        items = []
        page = 1

        while len(items) < total_items and page <= 3:
            results = self.discover_tv_by_genre(genre_id, page=page)
            if not results:
                break
            items.extend(results)
            page += 1

        return items[:total_items]