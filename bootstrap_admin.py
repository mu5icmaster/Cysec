# bootstrap_admin.py
from getpass import getpass
import re
from Database.Database import DatabaseConnection
from Database.Authentication import authentication

def email_ok(e: str) -> bool:
    return re.match(r"^[\w\-.]+@([\w-]+\.)+[\w-]{2,}$", e) is not None

def strong_pw(pw: str) -> bool:
    # minimal policy — tweak as you like
    return len(pw) >= 8 and any(c.isdigit() for c in pw) and any(c.isalpha() for c in pw)

def accounts_count(db: DatabaseConnection) -> int:
    db.cursor.execute("SELECT COUNT(*) FROM Accounts")
    return int(db.cursor.fetchone()[0])

def email_exists(db: DatabaseConnection, email: str) -> bool:
    db.cursor.execute("SELECT 1 FROM Accounts WHERE Email = ?", (email,))
    return db.cursor.fetchone() is not None

def main():
    db = DatabaseConnection()

    if accounts_count(db) > 0:
        print("[OK] Accounts already exist. No action required.")
        return

    print("=== First-run setup: Create Administrator account ===")
    # Admin meta
    while True:
        name = input("Admin full name: ").strip()
        if name:
            break
        print("Name cannot be empty.")

    while True:
        email = input("Admin email: ").strip().lower()
        if not email_ok(email):
            print("Please enter a valid email.")
            continue
        if email_exists(db, email):
            print("That email already exists. Choose another.")
            continue
        break

    while True:
        phone = input("Admin contact number (digits only, e.g., 60161234567): ").strip()
        if phone and phone.isdigit():
            break
        print("Please enter digits only.")

    # Secure password prompt/confirm
    while True:
        pw = getpass("New password: ")
        if not strong_pw(pw):
            print("Password must be at least 8 chars and include letters and numbers.")
            continue
        pw2 = getpass("Confirm password: ")
        if pw != pw2:
            print("Passwords do not match.")
            continue
        break

    # Create Admin (RoleID = 1)
    ok = authentication().createAccount(email, 1, name, phone, pw)
    if ok:
        print(f"[SUCCESS] Administrator created: {email}")
    else:
        print("[ERROR] Failed to create admin. Check logs for details.")

if __name__ == "__main__":
    main()
