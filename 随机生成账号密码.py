import random
import string

def generate_username(length=8):
    """Generate a random English username."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_password(length=12):
    """Generate a random password with letters, digits, and special characters."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

if __name__ == "__main__":
    username = generate_username()
    password = generate_password()
    print(f"Username: {username}")
    print(f"Password: {password}")