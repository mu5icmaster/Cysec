# Login.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from Database.Authentication import authentication


class Login(ttk.Frame):
    """
    Minimal, secure login screen:
    - Never prints credentials
    - Clears password immediately after authentication attempt
    - Calls onLogin_callback(self, email) on success (keeps your original contract)
    """

    def __init__(self, master: ttk.Window, onLogin_callback):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        self.onLogin_callback = onLogin_callback
        self.auth = authentication()

        self.textVariables = {
            "email": ttk.StringVar(),
            "password": ttk.StringVar(),
        }

        # UI
        card = ttk.Frame(self, padding=20, bootstyle="light")
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Sign in", font="-size 16 -weight bold").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(card, text="Email").grid(row=1, column=0, sticky="w")
        email_entry = ttk.Entry(card, textvariable=self.textVariables["email"], width=32)
        email_entry.grid(row=1, column=1, padx=(10, 0), pady=(2, 8))

        ttk.Label(card, text="Password").grid(row=2, column=0, sticky="w")
        pwd_entry = ttk.Entry(card, textvariable=self.textVariables["password"], show="*", width=32)
        pwd_entry.grid(row=2, column=1, padx=(10, 0), pady=(2, 8))

        self._error_label = ttk.Label(card, text="", bootstyle="danger")
        self._error_label.grid(row=3, column=0, columnspan=2, sticky="we")

        btn = ttk.Button(card, text="Login", bootstyle="success", command=self.onLogin)
        btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        email_entry.focus_set()

    # Kept name and behavior; just removed prints and added cleanup
    def onLogin(self):
        email = self.textVariables["email"].get().strip()
        password = self.textVariables["password"].get()

        try:
            if self.auth.authenticate(email, password):
                self._error_label.configure(text="")
                self.onLogin_callback(self, email)
            else:
                self._error_label.configure(text="Invalid Email or Password")
        finally:
            # Clear password regardless of outcome
            self.textVariables["password"].set("")
