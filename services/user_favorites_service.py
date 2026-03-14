from database import get_connection

def add_favorite_for_user(user_id, movie_data):
    connection = get_connection()
    cursor = connection.cursor()

    existing_favorite = cursor.execute(
        "SELECT * FROM favorites WHERE user_id = ? AND imdb_id = ?",
        (user_id, movie_data.get("imdb_id"))
    ).fetchone()

    if existing_favorite:
        connection.close()
        return False

    cursor.execute(
        """
        INSERT INTO favorites (
            user_id, imdb_id, title, year, poster, content_type,
            genre, plot, rating, runtime, actors,
            trailer_title, trailer_url, trailer_video_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
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
        )
    )

    connection.commit()
    connection.close()
    return True

def list_favorites_for_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    favorites = cursor.execute(
        "SELECT * FROM favorites WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    connection.close()
    return favorites

def remove_favorite_for_user(user_id, imdb_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM favorites WHERE user_id = ? AND imdb_id = ?",
        (user_id, imdb_id)
    )
    connection.commit()
    connection.close()