import re
import datetime
from werkzeug.security import generate_password_hash
from database import get_connection
from werkzeug.security import check_password_hash

def is_valid_email(email):
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        return re.match(pattern, email) is not None

def validate_password(password):
        if len(password) < 8:
                return "La password deve essere di almeno 8 caratteri"
        
        if len(password) > 16:
                return "La password non può superare i 16 caratteri"
        
        if not any(character.isupper() for character in password):
                return "La password deve contenere almeno una lettera maiuscola"
        
        if not any(character.isupper() for character in password):
                return "La password deve contenere almeno una lettere minuscola"
        
        special_characters = "!@#$%^&*()-_=+[]{}|;:,.<>?/"


        if not any(character in special_characters for character in password):
                return "La password deve contenere almeno un carattere speciale"
        
        return None



def user_exists(email, username):
        connection = get_connection()
        cursor = connection.cursor()
        existing_user = cursor.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            (email, username)
        ).fetchone()    
        connection.close()
        return existing_user

def create_user(first_name, last_name, email, username, password):
        hashed_password = generate_password_hash(password)

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, email, username, password_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (first_name, last_name, email, username, hashed_password)
        )
        connection.commit()
        connection.close()


        
def get_user_by_email_or_username(identifier):
    connection = get_connection()
    cursor = connection.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE email = ? OR username = ?",
        (identifier, identifier)
    ).fetchone()

    connection.close()
    return user



def verify_user_login(identifier, password):
    user = get_user_by_email_or_username(identifier)

    if user is None:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    return user

def get_user_by_email(email):
    connection = get_connection()
    cursor = connection.cursor()
    user = cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    connection.close()
    return user


def save_reset_token(user_id, token, expiry):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?",
        (token, expiry, user_id)
    )
    connection.commit()
    connection.close()


def get_user_by_reset_token(token):
    connection = get_connection()
    cursor = connection.cursor()
    user = cursor.execute(
        "SELECT * FROM users WHERE reset_token = ?",
        (token,)
    ).fetchone()
    connection.close()
    return user


def is_reset_token_expired(expiry_string):
    if not expiry_string:
        return True

    expiry_datetime = datetime.datetime.fromisoformat(expiry_string)
    return datetime.datetime.utcnow() > expiry_datetime


def update_user_password(user_id, new_password):
    hashed_password = generate_password_hash(new_password)

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE users
        SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL
        WHERE id = ?
        """,
        (hashed_password, user_id)
    )
    connection.commit()
    connection.close()