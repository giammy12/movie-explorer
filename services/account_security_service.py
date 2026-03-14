import datetime
import random

from database import get_connection


def generate_otp():
    return str(random.randint(100000, 999999))


def save_otp(user_id, otp_code, purpose):
    expiry = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM account_otps WHERE user_id = ? AND purpose = ?",
        (user_id, purpose)
    )

    cursor.execute(
        """
        INSERT INTO account_otps (user_id, otp_code, purpose, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, otp_code, purpose, expiry)
    )

    connection.commit()
    connection.close()


def get_valid_otp(user_id, otp_code, purpose):
    connection = get_connection()
    cursor = connection.cursor()

    otp_row = cursor.execute(
        """
        SELECT * FROM account_otps
        WHERE user_id = ? AND otp_code = ? AND purpose = ?
        """,
        (user_id, otp_code, purpose)
    ).fetchone()

    connection.close()
    return otp_row


def is_otp_expired(expiry_string):
    if not expiry_string:
        return True

    expiry_datetime = datetime.datetime.fromisoformat(expiry_string)
    return datetime.datetime.utcnow() > expiry_datetime


def delete_otp(user_id, purpose):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM account_otps WHERE user_id = ? AND purpose = ?",
        (user_id, purpose)
    )

    connection.commit()
    connection.close()