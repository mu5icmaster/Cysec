import re
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from Database.Authentication import authentication
from Database import Database


class AccountSetupDialog(ttk.Toplevel):
    """
    Create Account dialog.

    - Role dropdown is populated from DB (excludes Administrator).
    - Resolves role_id by role *name* selected.
    - Admins can choose role; non-admin flows can keep the role locked.

    Args:
        parent: tk parent window
        force_admin (bool): If True, role combobox is enabled.
        fixed_role (str|None): If provided, locks the role (e.g., "Worker" or "Supervisor").
        on_success (callable|None): Called with email on successful creation.
    """

    def __init__(self, parent, force_admin: bool = False, fixed_role: str | None = None, on_success=None):
        super().__init__(parent)
        self.title("Create Account")
        self.transient(parent)
        self.takefocus = True
        self.place_window_center()
        self.resizable(False, False)

        self.on_success = on_success
        self.auth = authentication()
        self.db = Database.DatabaseConnection()

        # ---- form model ----
        self.full_name = ttk.StringVar()
        self.email = ttk.StringVar()
        self.contact = ttk.StringVar()
        self.role = ttk.StringVar()
        self.password = ttk.StringVar()
        self.password2 = ttk.StringVar()

        # Dynamic role choices from DB (exact names)
        self.role_choices = self._get_role_choices()  # e.g. ["Worker","Supervisor"]
        default_role = "Worker" if "Worker" in self.role_choices else (self.role_choices[0] if self.role_choices else "Worker")

        # Decide role behavior
        if fixed_role and fixed_role in self.role_choices:
            self.role.set(fixed_role)
            self.role_disabled = True and not force_admin
        else:
            self.role.set(default_role)
            self.role_disabled = (not force_admin)  # locked unless admin

        # ---- layout ----
        pad = {"padx": (18, 18), "pady": (6, 6)}
        header = ttk.Label(self, text="Create Account", font="-size 16 -weight bold")
        header.grid(row=0, column=0, columnspan=2, pady=(14, 4))

        ttk.Label(self, text="Full Name").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.full_name, width=32).grid(row=1, column=1, sticky="we", **pad)

        ttk.Label(self, text="Email").grid(row=2, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.email, width=32).grid(row=2, column=1, sticky="we", **pad)

        ttk.Label(self, text="Contact Number").grid(row=3, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.contact, width=32).grid(row=3, column=1, sticky="we", **pad)

        ttk.Label(self, text="Role").grid(row=4, column=0, sticky="e", **pad)
        role_cb = ttk.Combobox(self, values=self.role_choices or ["Worker"], textvariable=self.role, width=29, state="readonly")
        role_cb.grid(row=4, column=1, sticky="we", **pad)
        if self.role_disabled:
            role_cb.configure(state="disabled")

        ttk.Label(self, text="Password").grid(row=5, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.password, show="*", width=32).grid(row=5, column=1, sticky="we", **pad)

        ttk.Label(self, text="Confirm Password").grid(row=6, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.password2, show="*", width=32).grid(row=6, column=1, sticky="we", **pad)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(10, 14))
        ttk.Button(btn_frame, text="Cancel", bootstyle="secondary", command=self.destroy).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Create Account", bootstyle="success", command=self._save).grid(row=0, column=1, padx=6)

        self.columnconfigure(1, weight=1)
        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self.destroy())

    # ---------- validation & save ----------

    def _validate(self) -> tuple[bool, str]:
        name = self.full_name.get().strip()
        email = self.email.get().strip()
        contact = self.contact.get().strip()
        role = (self.role.get() or "").strip()
        pw1 = self.password.get()
        pw2 = self.password2.get()

        if not name or not email or not contact or not pw1 or not pw2:
            return False, "Please fill in all fields."

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return False, "Please enter a valid email address."

        if not re.match(r"^[0-9+\-\s]{6,20}$", contact):
            return False, "Please enter a valid contact number."
        
        # At least 8 characters
        if len(pw1) < 8:
            return False, "Password must be at least 8 characters long."

        if pw1 != pw2:
            return False, "Passwords do not match."

        if role not in self.role_choices:
            return False, "Invalid role selected."

        return True, ""

    def _save(self):
        ok, msg = self._validate()
        if not ok:
            Messagebox.show_error(msg, "Validation Error", parent=self)
            return

        name = self.full_name.get().strip()
        email = self.email.get().strip()
        contact = self.contact.get().strip()
        role_name = self.role.get().strip()
        pw = self.password.get()

        role_id = self._lookup_role_id(role_name)
        if role_id is None:
            Messagebox.show_error("Could not resolve role id for selected role.", "Create Account", parent=self)
            return

        try:
            created = self.auth.createAccount(
                employeeEmail=email,
                employeeName=name,
                employeeRoleID=role_id,
                employeeContactNumber=contact,
                employeePassword=pw
            )
        except Exception as e:
            Messagebox.show_error(f"Failed to create account:\n{e}", "Database Error", parent=self)
            return

        if created is False:
            Messagebox.show_error("Could not create the account. It may already exist.", "Create Account", parent=self)
            return

        Messagebox.show_info(f"Account created for {email}.", "Create Account", parent=self)
        if callable(self.on_success):
            try:
                self.on_success(email)
            except Exception:
                pass
        self.destroy()

    # ---------- helpers ----------

    def _get_role_choices(self):
        """Return role names from Roles table, excluding Administrator-like entries."""
        names = []
        conn = getattr(self.db, "conn", None) or getattr(self.db, "connection", None)
        if conn is None:
            return ["Worker", "Supervisor"]
        cur = conn.cursor()
        try:
            attempts = [
                ("SELECT role_name FROM Roles", 0),
                ("SELECT RoleName FROM Roles", 0),
                ("SELECT name FROM roles", 0),
            ]
            for sql, idx in attempts:
                try:
                    cur.execute(sql)
                    rows = cur.fetchall()
                    if rows:
                        for r in rows:
                            n = str(r[idx]).strip()
                            if n and n.lower() not in ("administrator", "admin"):
                                names.append(n)
                        break
                except Exception:
                    continue
            # Deduplicate while preserving order
            seen = set()
            unique = []
            for n in names:
                if n.lower() not in seen:
                    seen.add(n.lower())
                    unique.append(n)
            return unique or ["Worker", "Supervisor"]
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def _lookup_role_id(self, role_name: str):
        """Resolve role_id by exact role name (case-insensitive)."""
        conn = getattr(self.db, "conn", None) or getattr(self.db, "connection", None)
        if conn is None:
            return None
        cur = conn.cursor()
        try:
            candidates = [
                ("Roles", "role_id", "role_name"),
                ("Roles", "RoleID", "RoleName"),
                ("roles", "id", "name"),
            ]
            for table, id_col, name_col in candidates:
                try:
                    cur.execute(f"SELECT {id_col} FROM {table} WHERE LOWER({name_col}) = LOWER(?)", (role_name,))
                    row = cur.fetchone()
                    if row:
                        return row[0]
                except Exception:
                    continue
            return None
        finally:
            try:
                cur.close()
            except Exception:
                pass
