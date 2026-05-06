#!/usr/bin/env python3
"""
Create an admin user manually.
Usage: python -m scripts.create_admin
"""
import asyncio
import sys
from pathlib import Path

# Allow running from server/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.constants import UserRole, VerificationStatus
from app.core.database import connect_db, disconnect_db
from app.core.security import hash_password
from app.models.user import User


async def create_admin(email: str, full_name: str, password: str) -> None:
    await connect_db()

    existing = await User.find_one(User.email == email.lower())
    if existing:
        print(f"[ERROR] User with email '{email}' already exists.")
        return

    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        full_name=full_name,
        role=UserRole.ADMIN,
        email_verified=True,
        verification_status=VerificationStatus.VERIFIED,
        is_active=True,
    )
    await user.insert()
    print(f"[OK] Admin created: {email} (id={user.id})")
    await disconnect_db()


def prompt_input() -> tuple[str, str, str]:
    print("=== Create Admin User ===")
    email = input("Email: ").strip()
    full_name = input("Full name: ").strip()
    password = input("Password: ").strip()
    return email, full_name, password


if __name__ == "__main__":
    email, full_name, password = prompt_input()
    asyncio.run(create_admin(email, full_name, password))
