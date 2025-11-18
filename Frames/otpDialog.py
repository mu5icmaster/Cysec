# Frames/otpDialog.py
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

class OtpDialog(ttk.Toplevel):
    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Enter OTP")
        self.resizable(False, False)
        self.grab_set()
        ttk.Label(self, text="A one-time password has been sent to your email.").pack(padx=16, pady=(16,8))
        self.var = ttk.StringVar()
        ttk.Entry(self, textvariable=self.var, width=12, justify="center").pack(padx=16, pady=6)
        btns = ttk.Frame(self); btns.pack(pady=(8,16))
        ttk.Button(btns, text="Cancel", bootstyle="secondary", command=self.destroy).pack(side="left", padx=6)
        ttk.Button(btns, text="Verify", bootstyle="success",
                   command=lambda: on_submit(self.var.get().strip(), self)).pack(side="left", padx=6)
