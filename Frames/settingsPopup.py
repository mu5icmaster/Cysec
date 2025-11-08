# Frames/settingsPopup.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from Database.Database import DatabaseConnection
from Database.Authentication import authentication


class SettingsPopup(ttk.Toplevel):
    """
    Secure Settings popup (password change):
    - Requires current password to change to a new one
    - Validates new == confirm
    - Clears sensitive StringVars after use
    """

    def __init__(self, parent: ttk.Window, employeeID: int, callback_function=None):
        super().__init__(title="Settings", takefocus=True, resizable=(False, False))
        self.parent = parent
        self.employeeID = employeeID
        self.callback_function = callback_function or (lambda: None)
        self.db = DatabaseConnection()
        self.auth = authentication()

        self.place_window_center()

        frm = ttk.Frame(self, padding=16)
        frm.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        ttk.Label(frm, text="Change Password", font="-size 14 -weight bold").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(frm, text="Current Password").grid(row=1, column=0, sticky="w", pady=2)
        self.var_current = ttk.StringVar()
        ent_current = ttk.Entry(frm, textvariable=self.var_current, show="*", width=32)
        ent_current.grid(row=1, column=1, sticky="ew")

        ttk.Label(frm, text="New Password").grid(row=2, column=0, sticky="w", pady=2)
        self.var_new = ttk.StringVar()
        ent_new = ttk.Entry(frm, textvariable=self.var_new, show="*", width=32)
        ent_new.grid(row=2, column=1, sticky="ew")

        ttk.Label(frm, text="Confirm New Password").grid(row=3, column=0, sticky="w", pady=2)
        self.var_confirm = ttk.StringVar()
        ent_confirm = ttk.Entry(frm, textvariable=self.var_confirm, show="*", width=32)
        ent_confirm.grid(row=3, column=1, sticky="ew")

        self.err = ttk.Label(frm, text="", bootstyle="danger")
        self.err.grid(row=4, column=0, columnspan=2, sticky="we")

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", bootstyle="secondary", command=self.destroy).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Update Password", bootstyle="success", command=self._on_submit).grid(row=0, column=1)

        for i in range(2):
            frm.columnconfigure(i, weight=1)

    def _clear_sensitive(self):
        self.var_current.set("")
        self.var_new.set("")
        self.var_confirm.set("")

    def _on_submit(self):
        new = self.var_new.get()
        confirm = self.var_confirm.get()
        current = self.var_current.get()

        if new != confirm:
            self.err.configure(text="Passwords do not match")
            return
        if len(new) < 8:
            self.err.configure(text="Password must be at least 8 characters")
            return

        # Verify current password
        email = self.db.query_employee(self.employeeID)[2]
        if not self.auth.authenticate(email, current):
            self.err.configure(text="Current password is incorrect")
            self.var_current.set("")
            return

        # Reset to new password
        self.auth.resetPassword(self.employeeID, new)
        self._clear_sensitive()

        self.callback_function()
        Messagebox.ok("Password successfully changed", "Success")
        self.destroy()

    # Utility from ttkbootstrap Toplevel
    def place_window_center(self):
        self.update_idletasks()
        w, h = 460, 240
        x = self.winfo_screenwidth() // 2 - w // 2
        y = self.winfo_screenheight() // 3 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
