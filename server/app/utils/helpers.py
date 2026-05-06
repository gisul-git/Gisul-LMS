from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def mask_email(email: str) -> str:
    """Mask email for safe logging: user@example.com → u***@example.com"""
    parts = email.split("@")
    if len(parts) != 2:
        return "***"
    local, domain = parts
    return f"{local[0]}***@{domain}"
