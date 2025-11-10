# Database/Authentication.py
import sqlite3
import bcrypt
from loguru import logger

from Database import singleton, DatabaseConnection


def _now():
    from datetime import datetime
    return datetime.now()


def _to_bytes(h):
    # sqlite might return bytes or str; bcrypt needs bytes
    if isinstance(h, bytes):
        return h
    if isinstance(h, memoryview):
        return bytes(h)
    if isinstance(h, str):
        return h.encode("utf-8")
    # last resort
    return bytes(h)


@singleton
class authentication:
    """
    Hardened authentication:
    - Normalizes email (strip + lower) on auth/create/update
    - bcrypt over UTF-8 password (modern)
    - Legacy fallback: bcrypt(base64(sha256(password)))
    - In-memory lockout after 5 bad tries for 5 minutes
    """

    def __init__(self):
        self.db_connection = DatabaseConnection()
        self._fail_counts: dict[str, int] = {}
        self._lock_until: dict[str, object] = {}

    # ---------- lockout helpers ----------

    def _norm_email(self, email: str) -> str:
        return (email or "").strip().lower()

    def _is_locked(self, email: str) -> bool:
        until = self._lock_until.get(email)
        return until is not None and _now() < until

    def _record_failure(self, email: str) -> None:
        from datetime import timedelta
        n = self._fail_counts.get(email, 0) + 1
        self._fail_counts[email] = n
        if n >= 5:
            self._lock_until[email] = _now() + timedelta(minutes=5)

    def _record_success(self, email: str) -> None:
        self._fail_counts.pop(email, None)
        self._lock_until.pop(email, None)

    def is_locked_out(self, email: str) -> bool:
        """Helper you can use for debugging."""
        return self._is_locked(self._norm_email(email))

    # ---------- password verify ----------

    @staticmethod
    def _bcrypt_check_utf8(raw_password: str, stored_hash: bytes) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), stored_hash)

    @staticmethod
    def _bcrypt_check_legacy(raw_password: str, stored_hash: bytes) -> bool:
        import base64, hashlib
        legacy = base64.b64encode(hashlib.sha256(raw_password.encode()).digest())
        return bcrypt.checkpw(legacy, stored_hash)

    def _check_password(self, raw_password: str, stored_hash) -> bool:
        sh = _to_bytes(stored_hash)
        # Current scheme
        try:
            if self._bcrypt_check_utf8(raw_password, sh):
                return True
        except Exception:
            pass
        # Legacy scheme
        try:
            return self._bcrypt_check_legacy(raw_password, sh)
        except Exception:
            return False

    # ---------- public API ----------

    def authenticate(self, email: str, password: str) -> bool:
        email = self._norm_email(email)
        # basic input hardening
        if not email or not isinstance(password, str) or password == "":
            return False

        if self._is_locked(email):
            return False

        cursor = self.db_connection.cursor
        cursor.execute("SELECT HashedPW FROM Accounts WHERE lower(Email) = ?", (email,))
        row = cursor.fetchone()
        if not row:
            self._record_failure(email)
            return False

        hashed = row[0]
        if self._check_password(password, hashed):
            employee_id = self.db_connection.query_employee_login(email)
            if employee_id is None:
                # Shouldn't happen if email matched; treat as fail
                self._record_failure(email)
                return False
            self.db_connection.log_employee(employee_id)
            self._record_success(email)
            logger.bind(id=str(employee_id)).success("Successful authentication", event="Authentication",
                                                     placeholder="", type="notification")
            return True
        

        self._record_failure(email)
        return False

    def resetPassword(self, employeeID: int, password: str) -> None:
        cursor = self.db_connection.cursor
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=14))
        try:
            cursor.execute("""UPDATE Accounts SET HashedPW = ? WHERE WorkerID = ?""", (hashed, employeeID,))
            self.db_connection.connection.commit()
        except sqlite3.Error as err:
            logger.error(f"Password reset failed: {err}")

    def createAccount(self, employeeEmail: str, employeeRoleID: int, employeeName: str,
                      employeeContactNumber: str, employeePassword: str) -> bool:
        email = self._norm_email(employeeEmail)
        cursor = self.db_connection.cursor
        hashed = bcrypt.hashpw(employeePassword.encode("utf-8"), bcrypt.gensalt(rounds=14))

        try:
            cursor.execute("""INSERT INTO Workers (RoleID, Name, ContactNumber)
                              VALUES (?, ?, ?)""", (employeeRoleID, employeeName, employeeContactNumber,))
            employeeID = cursor.lastrowid
            cursor.execute("""INSERT INTO Accounts (WorkerID, Email, HashedPW)
                              VALUES (?, ?, ?)""", (employeeID, email, hashed,))
            self.db_connection.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Create account error: {e}")
            return False

    def updateAccount(self, employeeEmail: str, employeeRoleID: int, employeeName: str,
                      employeeContactNumber: str, employeePassword: str, employeeID: int) -> bool:
        email = self._norm_email(employeeEmail)
        cursor = self.db_connection.cursor
        hashed = bcrypt.hashpw(employeePassword.encode("utf-8"), bcrypt.gensalt(rounds=14))

        try:
            cursor.execute("""UPDATE Workers
                              SET RoleID = ?, Name = ?, ContactNumber = ?
                              WHERE WorkerID = ?""",
                           (employeeRoleID, employeeName, employeeContactNumber, employeeID,))
            cursor.execute("""UPDATE Accounts
                              SET Email = ?, HashedPW = ?
                              WHERE WorkerID = ?""",
                           (email, hashed, employeeID))
            self.db_connection.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Update account error: {e}")
            return False
