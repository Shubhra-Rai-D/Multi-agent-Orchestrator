import os
from dotenv import load_dotenv
from utils.database import init_db, user_count, insert_user, fetch_all_users

load_dotenv()

# System-level API key (stays in .env — not per-user)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ──────────────────────────────────────────────
# Database Initialization & Seeding from .env
# ──────────────────────────────────────────────
init_db()

# On first run (empty database), seed users from .env variables
if user_count() == 0:
    DEFAULT_NAMES = {1: "Alice", 2: "Bob"}
    user_num = 1
    while True:
        token       = os.getenv(f"GITHUB_TOKEN_USER{user_num}")
        username    = os.getenv(f"GITHUB_USERNAME_USER{user_num}")
        linear_key  = os.getenv(f"LINEAR_API_KEY_USER{user_num}")
        linear_user = os.getenv(f"LINEAR_USERNAME_USER{user_num}")

        # Stop when no credentials exist for this user number
        if not any([token, username, linear_key, linear_user]):
            break

        name = DEFAULT_NAMES.get(user_num, f"User{user_num}")
        insert_user(f"user{user_num}", name, token, username, linear_key, linear_user)
        user_num += 1

# ──────────────────────────────────────────────
# Load users from database (runtime source of truth)
# ──────────────────────────────────────────────
USERS_CONFIG = fetch_all_users()


def reload_users():
    """Refresh USERS_CONFIG from database after adding a new user."""
    global USERS_CONFIG
    USERS_CONFIG = fetch_all_users()


# ──────────────────────────────────────────────
# Helper Functions (used by orchestrator & agents)
# ──────────────────────────────────────────────

def get_user_config(user_id: str):
    """
    Returns the configuration dictionary for the specified user_id.
    """
    return USERS_CONFIG.get(user_id)


def get_available_users():
    """
    Returns a list of user names available in the system.
    """
    return [info["name"] for info in USERS_CONFIG.values() if info.get("name")]


def get_available_users_str():
    """
    Returns a formatted string of available user names, e.g. 'Alice, Bob'.
    """
    users = get_available_users()
    return ", ".join(users) if users else "None"


def get_user_id_by_name(query: str):
    """
    Scans the query for user names (case-insensitive) in USERS_CONFIG or user IDs.
    Returns the user_id if found, else None.
    """
    query_lower = query.lower()
    for user_id, config in USERS_CONFIG.items():
        name = config.get("name", "").lower()
        if name and name in query_lower:
            return user_id
        if user_id.lower() in query_lower:
            return user_id
    return None


def get_user_name(user_id: str):
    """
    Returns the display name for a given user_id.
    """
    config = USERS_CONFIG.get(user_id)
    return config.get("name", user_id) if config else user_id


def get_user_mapping_str():
    """
    Returns a dynamic mapping string for the LLM prompt,
    e.g. 'Alice = target_user "user1", Bob = target_user "user2"'
    """
    parts = []
    for user_id, config in USERS_CONFIG.items():
        name = config.get("name", user_id)
        parts.append(f'{name} = target_user "{user_id}"')
    return ", ".join(parts)


# ──────────────────────────────────────────────
# Interactive User Management
# ──────────────────────────────────────────────

def add_user():
    """
    Interactively prompts for a new user's credentials,
    saves them to the SQLite database, and refreshes the in-memory config.
    """
    next_num = user_count() + 1
    user_id = f"user{next_num}"

    print(f"\n--- Add New User (will be registered as '{user_id}') ---")

    name = input("  Display name (e.g. Charlie): ").strip()
    if not name:
        print("  Cancelled — name cannot be empty.")
        return None

    github_token    = input("  GitHub Token (or Enter to skip): ").strip() or None
    github_username = input("  GitHub Username (or Enter to skip): ").strip() or None
    linear_api_key  = input("  Linear API Key (or Enter to skip): ").strip() or None
    linear_username = input("  Linear Username (or Enter to skip): ").strip() or None

    insert_user(user_id, name, github_token, github_username, linear_api_key, linear_username)
    reload_users()

    print(f"  ✓ {name} saved to database as {user_id}!\n")
    return name


def list_users():
    """Prints all registered users and their configured integrations."""
    if not USERS_CONFIG:
        print("  No users registered.\n")
        return

    print(f"\n  Registered Users ({len(USERS_CONFIG)}):")
    for user_id, config in USERS_CONFIG.items():
        name = config.get("name", user_id)
        has_github = "✓" if config.get("github_token") else "✗"
        has_linear = "✓" if config.get("linear_api_key") else "✗"
        print(f"    {user_id}: {name}  [GitHub: {has_github}] [Linear: {has_linear}]")
    print()
