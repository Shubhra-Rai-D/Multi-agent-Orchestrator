import sqlite3
import os

# Database file sits in the project root (same level as main.py)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users.db")


def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Creates the users table if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                github_token TEXT,
                github_username TEXT,
                linear_api_key TEXT,
                linear_username TEXT
            )
        """)


def user_count():
    """Returns the total number of registered users."""
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def insert_user(user_id, name, github_token=None, github_username=None,
                linear_api_key=None, linear_username=None):
    """Inserts a new user into the database. Skips silently if user_id already exists."""
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO users
            (user_id, name, github_token, github_username, linear_api_key, linear_username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, github_token, github_username, linear_api_key, linear_username))


def fetch_all_users():
    """
    Loads all users from the database and returns them as a dictionary
    matching the USERS_CONFIG format used throughout the application.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT user_id, name, github_token, github_username, "
            "linear_api_key, linear_username FROM users"
        )
        users = {}
        for row in cursor.fetchall():
            users[row[0]] = {
                "name": row[1],
                "github_token": row[2],
                "github_username": row[3],
                "linear_api_key": row[4],
                "linear_username": row[5],
            }
        return users
