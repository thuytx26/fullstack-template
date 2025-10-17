import random
import string


def random_lower_string(k=32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))


def random_username() -> str:
    return random_lower_string(k=16)


def random_password() -> str:
    return random_lower_string(k=8)
