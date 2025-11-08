# Frames/accountSetupDialog.py
import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from Database.Authentication import authentication

# at the top of the file (keep existing imports/constants)
ROLE_MAP = {
    "Administrator": 1,
    "Supervisor": 2,
    "Worker": 3,
}

class AccountSetupDialog(ttk.Toplevel):
    """
    Reusable account creation dialog.
    - force_admin=True  -> role fixed to Administrator
    - fixed_role="Worker"/"Supervisor"/"Administrator" -> role fixed to that value
    - If neither is set, user can choose the role.
    Calls `on_success(email)` when an account is created successfully.
    """

    def __init__(self, parent, force_admin: bool = False, fixed_role: str | None = None, on_success=None):
        super().__init__(parent)
        self.title("Create Account")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_success = on_success or (lambda email: None)
        self.auth = authentication()
        self.force_admin = force_admin
        self.fixed_role = (fixed_role if fixed_role in ROLE_MAP else None)

        frame = ttk.Frame(self, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        ttk.Label(frame, text="Create Account", font="-size 14 -weight bold").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Name
        ttk.Label(frame, text="Full Name").grid(row=1, column=0, sticky="w")
        self.var_name = ttk.StringVar()
        ttk.Entry(frame, textvariable=self.var_name, width=34).grid(row=1, column=1, sticky="ew", pady=4)

        # Email
        ttk.Label(frame, text="Email").grid(row=2, column=0, sticky="w")
        self.var_email = ttk.StringVar()
        ttk.Entry(frame, textvariable=self.var_email, width=34).grid(row=2, column=1, sticky="ew", pady=4)

        # Phone
        ttk.Label(frame, text="Contact Number").grid(row=3, column=0, sticky="w")
        self.var_phone = ttk.StringVar()
        ttk.Entry(frame, textvariable=self.var_phone, width=34).grid(row=3, column=1, sticky="ew", pady=4)

        # Role
        ttk.Label(frame, text="Role").grid(row=4, column=0, sticky="w")
        default_role = "Administrator" if self.force_admin else (self.fixed_role or "Worker")
        self.var_role = ttk.StringVar(value=default_role)
        role_values = ["Administrator", "Supervisor", "Worker"]
        self.role_widget = ttk.Combobox(frame, textvariable=self.var_role, values=role_values, state="readonly", width=32)
        self.role_widget.grid(row=4, column=1, sticky="ew", pady=4)
        if self.force_admin or self.fixed_role:
            self.role_widget.configure(state="disabled")

        # Passwords
        ttk.Label(frame, text="Password").grid(row=5, column=0, sticky="w")
        self.var_pw = ttk.StringVar()
        ttk.Entry(frame, textvariable=self.var_pw, show="*", width=34).grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Confirm Password").grid(row=6, column=0, sticky="w")
        self.var_pw2 = ttk.StringVar()
        ttk.Entry(frame, textvariable=self.var_pw2, show="*", width=34).grid(row=6, column=1, sticky="ew", pady=4)

        # Error label
        self.err = ttk.Label(frame, text="", bootstyle="danger")
        self.err.grid(row=7, column=0, columnspan=2, sticky="we")

        # Buttons
        btns = ttk.Frame(frame)
        btns.grid(row=8, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", bootstyle="secondary", command=self._on_cancel).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Create", bootstyle="success", command=self._on_create).grid(row=0, column=1)

        self._center(480, 300)
        self.wait_visibility()
        self.focus_force()


    def _center(self, w: int, h: int):
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - w // 2
        y = self.winfo_screenheight() // 3 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_cancel(self):
        self.destroy()

    def _on_create(self):
        role_name = "Administrator" if self.force_admin else (self.fixed_role or role_name)
        role_id = ROLE_MAP.get(role_name, 3)
        name = self.var_name.get().strip()
        email = (self.var_email.get() or "").strip().lower()
        phone = self.var_phone.get().strip()
        role_name = self.var_role.get().strip()
        pw = self.var_pw.get()
        pw2 = self.var_pw2.get()

        # validate
        if not name:
            self.err.configure(text="Name is required.")
            return
        if not email_ok(email):
            self.err.configure(text="Enter a valid email.")
            return
        if not phone.isdigit():
            self.err.configure(text="Contact number must be digits only.")
            return
        if pw != pw2:
            self.err.configure(text="Passwords do not match.")
            return
        if not strong_pw(pw):
            self.err.configure(text="Password must be ≥8 chars and include letters and numbers.")
            return

        # enforce Admin role when forced
        if self.force_admin:
            role_name = "Administrator"

        role_id = ROLE_MAP.get(role_name, 3)

        ok = self.auth.createAccount(email, role_id, name, phone, pw)
        if ok:
            # clear secrets
            self.var_pw.set("")
            self.var_pw2.set("")
            Messagebox.ok(f"{role_name} account created for: {email}", "Success")
            try:
                self.on_success(email)
            finally:
                self.destroy()
        else:
            self.err.configure(text="Failed to create account. Email may already exist.")
