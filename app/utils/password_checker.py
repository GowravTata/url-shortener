import bcrypt


def get_password_hash(password):
    """Hash a plaintext password using bcrypt and return the string-encoded hash."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode("utf8")
    return string_password


def verify_password(plain_password, hashed_password):
    """Return True if the plaintext password matches the bcrypt-hashed password."""
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_byte_enc, hashed_password)
