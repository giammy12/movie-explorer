from database import get_connection


def get_profiles_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, name, avatar_url, created_at
        FROM user_profiles
        WHERE user_id = ?
        ORDER BY created_at ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_profile_by_id_for_user(profile_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, name, avatar_url, created_at
        FROM user_profiles
        WHERE id = ? AND user_id = ?
        LIMIT 1
    """, (profile_id, user_id))

    row = cursor.fetchone()
    conn.close()
    return row


def create_profile_for_user(user_id, name, avatar_url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_profiles (user_id, name, avatar_url)
        VALUES (?, ?, ?)
    """, (user_id, name, avatar_url))

    conn.commit()
    profile_id = cursor.lastrowid
    conn.close()

    return get_profile_by_id_for_user(profile_id, user_id)


def count_profiles_for_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM user_profiles
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()
    return row["total"] if row else 0