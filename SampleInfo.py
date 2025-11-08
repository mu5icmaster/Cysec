# SampleInfo.py
"""
Development-only sample data seeder.

- Guarded by KEAI_ENV=development
- Generates strong random passwords for any seeded accounts
"""

import os
import secrets
import string

from Database.Database import DatabaseConnection
from Database.Authentication import authentication


def _strong_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def main():
    if os.getenv("KEAI_ENV", "development") != "development":
        raise SystemExit("Sample seeding is disabled outside development.")

    db = DatabaseConnection()
    auth = authentication()

    # Example seed: Administrator / Supervisor / Worker
    seeds = [
        ("admin@example.com", 1, "Admin User", "60161230001"),
        ("supervisor@example.com", 2, "Supervisor User", "60161230002"),
        ("worker@example.com", 3, "Worker User", "60161230003"),
    ]

    for email, role, name, phone in seeds:
        pw = _strong_password()
        if auth.createAccount(email, role, name, phone, pw):
            print(f"[DEV ONLY] Created {email} with password: {pw}")
        else:
            print(f"[DEV ONLY] Skipped/failed for {email} (may already exist)")


if __name__ == "__main__":
    main()
