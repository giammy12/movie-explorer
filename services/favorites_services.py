from database import get_connection


def _ensure_profile_column():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(favorites)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "profile_id" not in columns:
        try:
            cursor.execute("ALTER TABLE favorites ADD COLUMN profile_id INTEGER")
            conn.commit()
        except Exception:
            pass

    conn.close()


def add_favorite_for_user(user_id, movie_data, profile_id=None):
    _ensure_profile_column()

    conn = get_connection()
    cursor = conn.cursor()

    imdb_id = movie_data.get("imdb_id", "").strip()
    if not imdb_id:
        conn.close()
        return False

    if profile_id is not None:
        cursor.execute("""
            SELECT id
            FROM favorites
            WHERE user_id = ? AND profile_id = ? AND imdb_id = ?
            LIMIT 1
        """, (user_id, profile_id, imdb_id))
    else:
        cursor.execute("""
            SELECT id
            FROM favorites
            WHERE user_id = ? AND imdb_id = ? AND (profile_id IS NULL OR profile_id = '')
            LIMIT 1
        """, (user_id, imdb_id))

    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO favorites (
            user_id,
            profile_id,
            imdb_id,
            title,
            year,
            poster,
            content_type,
            genre,
            plot,
            rating,
            runtime,
            actors,
            trailer_title,
            trailer_url,
            trailer_video_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        profile_id,
        movie_data.get("imdb_id", ""),
        movie_data.get("title", ""),
        movie_data.get("year", ""),
        movie_data.get("poster", ""),
        movie_data.get("content_type", ""),
        movie_data.get("genre", ""),
        movie_data.get("plot", ""),
        movie_data.get("rating", ""),
        movie_data.get("runtime", ""),
        movie_data.get("actors", ""),
        movie_data.get("trailer_title", ""),
        movie_data.get("trailer_url", ""),
        movie_data.get("trailer_video_id", "")
    ))

    conn.commit()
    conn.close()
    return True


def list_favorites_for_user(user_id, profile_id=None):
    _ensure_profile_column()

    conn = get_connection()
    cursor = conn.cursor()

    if profile_id is not None:
        cursor.execute("""
            SELECT *
            FROM favorites
            WHERE user_id = ? AND profile_id = ?
            ORDER BY created_at DESC
        """, (user_id, profile_id))
    else:
        cursor.execute("""
            SELECT *
            FROM favorites
            WHERE user_id = ? AND (profile_id IS NULL OR profile_id = '')
            ORDER BY created_at DESC
        """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def remove_favorite_for_user(user_id, imdb_id, profile_id=None):
    _ensure_profile_column()

    conn = get_connection()
    cursor = conn.cursor()

    if profile_id is not None:
        cursor.execute("""
            DELETE FROM favorites
            WHERE user_id = ? AND profile_id = ? AND imdb_id = ?
        """, (user_id, profile_id, imdb_id))
    else:
        cursor.execute("""
            DELETE FROM favorites
            WHERE user_id = ? AND imdb_id = ? AND (profile_id IS NULL OR profile_id = '')
        """, (user_id, imdb_id))

    conn.commit()
    conn.close()