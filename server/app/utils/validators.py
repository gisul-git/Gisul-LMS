import re

from app.core.constants import PASSWORD_REGEX


def is_valid_password(password: str) -> bool:
    return bool(re.match(PASSWORD_REGEX, password))


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Strip leading/trailing whitespace and truncate."""
    return value.strip()[:max_length]
