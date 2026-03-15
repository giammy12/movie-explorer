from database import get_connection


def get_watch_record(user_id, profile_id, tmdb_id, content_type="movie", season=None, episode=None):
    conn = get_connection()
    cursor = conn.cursor()

    if content_type == "tv":
        cursor.execute("""
            SELECT *
            FROM watch_history
            WHERE user_id = ?
              AND profile_id = ?
              AND tmdb_id = ?
              AND content_type = ?
              AND season = ?
              AND episode = ?
            LIMIT 1
        """, (user_id, profile_id, tmdb_id, content_type, season, episode))
    else:
        cursor.execute("""
            SELECT *
            FROM watch_history
            WHERE user_id = ?
              AND profile_id = ?
              AND tmdb_id = ?
              AND content_type = ?
            LIMIT 1
        """, (user_id, profile_id, tmdb_id, content_type))

    row = cursor.fetchone()
    conn.close()
    return row


def prune_continue_watching(user_id, profile_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM watch_history
        WHERE user_id = ? AND profile_id = ? AND completed = 0
        ORDER BY updated_at DESC
    """, (user_id, profile_id))

    rows = cursor.fetchall()

    if len(rows) > limit:
        ids_to_delete = [row["id"] for row in rows[limit:]]
        placeholders = ",".join(["?"] * len(ids_to_delete))

        cursor.execute(
            f"DELETE FROM watch_history WHERE id IN ({placeholders})",
            ids_to_delete
        )

    conn.commit()
    conn.close()


def create_or_get_watch_record(
    user_id,
    profile_id,
    tmdb_id,
    title,
    poster_path,
    content_type="movie",
    season=None,
    episode=None
):
    existing = get_watch_record(
        user_id,
        profile_id,
        tmdb_id,
        content_type=content_type,
        season=season,
        episode=episode
    )

    if existing:
        conn = get_connection()
        cursor = conn.cursor()

        if content_type == "tv":
            cursor.execute("""
                UPDATE watch_history
                SET updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                  AND profile_id = ?
                  AND tmdb_id = ?
                  AND content_type = ?
                  AND season = ?
                  AND episode = ?
            """, (user_id, profile_id, tmdb_id, content_type, season, episode))
        else:
            cursor.execute("""
                UPDATE watch_history
                SET updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                  AND profile_id = ?
                  AND tmdb_id = ?
                  AND content_type = ?
            """, (user_id, profile_id, tmdb_id, content_type))

        conn.commit()
        conn.close()

        prune_continue_watching(user_id, profile_id, limit=5)

        return get_watch_record(
            user_id,
            profile_id,
            tmdb_id,
            content_type=content_type,
            season=season,
            episode=episode
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO watch_history (
            user_id,
            profile_id,
            tmdb_id,
            content_type,
            title,
            poster_path,
            season,
            episode,
            progress_seconds,
            duration_seconds,
            completed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
    """, (
        user_id,
        profile_id,
        tmdb_id,
        content_type,
        title,
        poster_path,
        season,
        episode
    ))

    conn.commit()
    conn.close()

    prune_continue_watching(user_id, profile_id, limit=5)

    return get_watch_record(
        user_id,
        profile_id,
        tmdb_id,
        content_type=content_type,
        season=season,
        episode=episode
    )


def update_watch_progress(
    user_id,
    profile_id,
    tmdb_id,
    progress_seconds,
    duration_seconds,
    content_type="movie",
    season=None,
    episode=None
):
    completed = 0

    if duration_seconds and progress_seconds:
        if duration_seconds - progress_seconds <= 60:
            completed = 1

    conn = get_connection()
    cursor = conn.cursor()

    if content_type == "tv":
        cursor.execute("""
            UPDATE watch_history
            SET progress_seconds = ?,
                duration_seconds = ?,
                completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
              AND profile_id = ?
              AND tmdb_id = ?
              AND content_type = ?
              AND season = ?
              AND episode = ?
        """, (
            progress_seconds,
            duration_seconds,
            completed,
            user_id,
            profile_id,
            tmdb_id,
            content_type,
            season,
            episode
        ))
    else:
        cursor.execute("""
            UPDATE watch_history
            SET progress_seconds = ?,
                duration_seconds = ?,
                completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
              AND profile_id = ?
              AND tmdb_id = ?
              AND content_type = ?
        """, (
            progress_seconds,
            duration_seconds,
            completed,
            user_id,
            profile_id,
            tmdb_id,
            content_type
        ))

    conn.commit()
    conn.close()

    prune_continue_watching(user_id, profile_id, limit=5)


def mark_watch_completed(user_id, profile_id, tmdb_id, content_type="movie", season=None, episode=None):
    conn = get_connection()
    cursor = conn.cursor()

    if content_type == "tv":
        cursor.execute("""
            UPDATE watch_history
            SET completed = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
              AND profile_id = ?
              AND tmdb_id = ?
              AND content_type = ?
              AND season = ?
              AND episode = ?
        """, (user_id, profile_id, tmdb_id, content_type, season, episode))
    else:
        cursor.execute("""
            UPDATE watch_history
            SET completed = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
              AND profile_id = ?
              AND tmdb_id = ?
              AND content_type = ?
        """, (user_id, profile_id, tmdb_id, content_type))

    conn.commit()
    conn.close()


def get_continue_watching(user_id, profile_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tmdb_id,
            content_type,
            title,
            poster_path,
            season,
            episode,
            progress_seconds,
            duration_seconds,
            completed
        FROM watch_history
        WHERE user_id = ? AND profile_id = ? AND completed = 0
        ORDER BY updated_at DESC
        LIMIT ?
    """, (user_id, profile_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows