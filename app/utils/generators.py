import random
import string

BASE62_CHARS = string.ascii_letters + string.digits


def generate_code(length: int = 7) -> str:
    """
    Generate a random Base62 short code.
    """
    return "".join(random.choices(BASE62_CHARS, k=length))
