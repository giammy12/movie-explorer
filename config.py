import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_FILE = os.path.join(DATA_DIR, "cache.json")
FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")

if not OMDB_API_KEY:
    raise ValueError("OMDB_API_KEY mancante nel file .env")

if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY mancante nel file .env")

if not FLASK_SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY mancante nel file .env")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY mancante nel file .env")

if not SMTP_HOST:
    raise ValueError("SMTP_HOST mancante nel file .env")

if not SMTP_USERNAME:
    raise ValueError("SMTP_USERNAME mancante nel file .env")

if not SMTP_PASSWORD:
    raise ValueError("SMTP_PASSWORD mancante nel file .env")

if not SMTP_FROM:
    raise ValueError("SMTP_FROM mancante nel file .env")