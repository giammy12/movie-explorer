from database import get_connection


def save_recent_search(user_id, query):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO recent_searches (user_id, query) VALUES (?, ?)",
        (user_id, query)
    )

    connection.commit()
    connection.close()


def get_recent_searches(user_id, limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    searches = cursor.execute(
        """
        SELECT * FROM recent_searches
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()

    connection.close()
    return searches


def delete_user_account(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM recent_searches WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    connection.commit()
    connection.close()