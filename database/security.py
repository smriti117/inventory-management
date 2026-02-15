import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def generate_hash(password: str):
    """Alias for get_password_hash for compatibility"""
    return get_password_hash(password)


def verify_hash(hashed_password: str, password: str):
    """Verify a password against a hash using bcrypt (replaces werkzeug for consistency)"""
    return verify_password(password, hashed_password)
