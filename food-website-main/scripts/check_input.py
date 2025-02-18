import re
from scripts.db import get_user

def sanitize_input(input_string):
    # Remove leading and trailing spaces
    sanitized_input = input_string.strip()
    # Prevent SQL injection by removing special characters
    sanitized_input = re.sub(r'[(;\'"\\)]', '', sanitized_input)
    return sanitized_input


def is_valid_username(username):
    # Rule 1: Username Length (between 3 and 20 characters)
    if 3 <= len(username) <= 20:
        # Rule 2: Character Set (alphanumeric characters, underscores, or hyphens)
        if re.match("^[a-zA-Z0-9_-]*$", username):
            # Rule 3: Uniqueness (Check if the username is unique in the database)
            # Implement the get_user function
            existing_user = get_user(username)
            if not existing_user:
                return True  # Valid username
            return False  # Username already exists
    return False  # Invalid username


def is_valid_password(password):
    # Rule 1: Password Length (at least 8 characters)
    if len(password) >= 4:
        # Rule 2: Complexity (requires at least one uppercase letter, one lowercase letter, one digit, and one special character)
        if re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!]).*$", password):
            # Rule 3: No Common Passwords (you can maintain a list of common passwords to check against)
            common_passwords = ["password", "123456", "qwerty", "admin"]
            if password not in common_passwords:
                return True  # Valid password
    return False  # Invalid password
