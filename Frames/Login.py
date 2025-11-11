import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import bcrypt

from Database.Authentication import authentication
from Database import Database
from utils_otp import generate_otp, hash_otp, send_otp_email, OTP_TTL, now
from Frames.otpDialog import OtpDialog


class Login(ttk.Frame):
    """
    Sign-in screen.
    On success calls: onLogin_callback(self, {"employee_id": int, "email": str})
    """

    def __init__(self, master: ttk.Window, onLogin_callback):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.onLogin_callback = onLogin_callback
        self.auth = authentication()
        self.db = Database.DatabaseConnection()

        self.text = {
            "email": ttk.StringVar(),
            "password": ttk.StringVar(),
        }

        container = ttk.Frame(self, bootstyle="light")
        container.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        card = ttk.Frame(container, padding=20, bootstyle="light")
        card.grid(row=0, column=0)

        ttk.Label(card, text="Sign in", font="-size 16 -weight bold").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(card, text="Email").grid(row=1, column=0, sticky="w")
        email_entry = ttk.Entry(card, textvariable=self.text["email"], width=32)
        email_entry.grid(row=1, column=1, padx=(10, 0), pady=(2, 8))

        ttk.Label(card, text="Password").grid(row=2, column=0, sticky="w")
        pwd_entry = ttk.Entry(card, textvariable=self.text["password"], show="*", width=32)
        pwd_entry.grid(row=2, column=1, padx=(10, 0), pady=(2, 8))

        self._error = ttk.Label(card, text="", bootstyle="danger")
        self._error.grid(row=3, column=0, columnspan=2, sticky="we")

        ttk.Button(card, text="Login", bootstyle="success", command=self.onLogin)\
            .grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        email_entry.focus_set()

    def onLogin(self):
        email = self.text["email"].get().strip()
        password = self.text["password"].get()

        try:
        # 1) 账号密码校验
            if not self.auth.authenticate(email, password):
                self._error.configure(text="Invalid Email or Password")
                return

        # 2) 获取员工ID（沿用你原来的两步）
            emp_id = self._get_emp_id_from_auth()
            if emp_id is None:
                emp_id = self._lookup_worker_id_by_email(email)
            if emp_id is None:
                self._error.configure(text="Unable to load user profile.")
                return

        # 3) 清理过期 OTP（容错）
            try:
                self.db.otp_cleanup()
            except Exception:
                pass

        # 4) 生成并发送 OTP（只发送明文，不入库）
            otp_plain = generate_otp()
            send_otp_email(email, otp_plain)
            self.db.otp_insert(emp_id, hash_otp(otp_plain), OTP_TTL)

        # 5) 弹出 OTP 对话框，验证通过后放行
            def _verify_cb(user_input: str, dialog):
                row = self.db.otp_get_latest_active(emp_id)
                if not row:
                    Messagebox.show_error("OTP expired. Please login again.", "OTP")
                    dialog.destroy(); return

                otp_id, code_hash, expires_at, attempts = row

                if now() > int(expires_at):
                    Messagebox.show_error("OTP expired. Please login again.", "OTP")
                    dialog.destroy(); return

                if attempts >= 3:
                    Messagebox.show_error("Too many attempts. Please login again.", "OTP")
                    dialog.destroy(); return

                ch = code_hash.encode() if isinstance(code_hash, str) else code_hash
                if bcrypt.checkpw(user_input.encode(), ch):
                    self.db.otp_consume(otp_id)
                    dialog.destroy()
                    user_ctx = {"employee_id": int(emp_id), "email": email}
                    self._error.configure(text="")
                    self.onLogin_callback(self, user_ctx)
                else:
                    self.db.otp_inc_attempt(otp_id)
                    Messagebox.show_error("Invalid OTP. Please try again.", "OTP")

            OtpDialog(self, _verify_cb)

        finally:
        # 不论成功失败都清空密码框，避免留在内存
            self.text["password"].set("")


    # ---------- helpers ----------

    def _conn(self):
        return getattr(self.db, "conn", None) or getattr(self.db, "connection", None)

    def _get_emp_id_from_auth(self):
        # If your Authentication class stores the last id, use it.
        if hasattr(self.auth, "get_last_employee_id"):
            try:
                v = self.auth.get_last_employee_id()
                return int(v) if v is not None else None
            except Exception:
                pass
        for attr in ("last_employee_id", "employee_id", "employeeID", "_employee_id", "_employeeID"):
            if hasattr(self.auth, attr):
                try:
                    v = getattr(self.auth, attr)
                    return int(v) if v is not None else None
                except Exception:
                    continue
        return None

    def _lookup_worker_id_by_email(self, email: str):
        """
        Your schema: Accounts(WorkerID, Email, HashedPW)
        """
        conn = self._conn()
        if conn is None:
            return None
        cur = conn.cursor()
        try:
            cur.execute("SELECT WorkerID FROM Accounts WHERE LOWER(Email)=LOWER(?)", (email,))
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else None
        except Exception:
            return None
        finally:
            cur.close()
