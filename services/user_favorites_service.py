from database import get_connection


def add_favorite_for_user(user_id, movie_data, profile_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    imdb_id = movie_data.get("imdb_id")

    cursor.execute("""
        SELECT id
        FROM favorites
        WHERE user_id = ?
        AND imdb_id = ?
        AND profile_id IS ?
    """, (user_id, imdb_id, profile_id))

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
            content_type,
            genre,
            plot,
            rating,
            runtime,
            actors,
            poster,
            trailer_title,
            trailer_url,
            trailer_video_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        profile_id,
        imdb_id,
        movie_data.get("title"),
        movie_data.get("year"),
        movie_data.get("content_type"),
        movie_data.get("genre"),
        movie_data.get("plot"),
        movie_data.get("rating"),
        movie_data.get("runtime"),
        movie_data.get("actors"),
        movie_data.get("poster"),
        movie_data.get("trailer_title"),
        movie_data.get("trailer_url"),
        movie_data.get("trailer_video_id")
    ))

    conn.commit()
    conn.close()

    return True


def list_favorites_for_user(user_id, profile_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM favorites
        WHERE user_id = ?
        AND profile_id IS ?
        ORDER BY id DESC
    """, (user_id, profile_id))

    rows = cursor.fetchall()
    conn.close()

    return rows


def remove_favorite_for_user(user_id, imdb_id, profile_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM favorites
        WHERE user_id = ?
        AND imdb_id = ?
        AND profile_id IS ?
    """, (user_id, imdb_id, profile_id))

    conn.commit()
    conn.close()