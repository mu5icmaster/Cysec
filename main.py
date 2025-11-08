import sys
import ttkbootstrap as ttk

from Frames import *
from Frames.navigationFrame import navigationFrame
from Frames.accountSetupDialog import AccountSetupDialog  # <-- NEW
from Database.Database import DatabaseConnection


def _ensure_admin_gui(window) -> None:
    """If no accounts exist, block with a modal to create the first Admin."""
    db = DatabaseConnection()
    db.cursor.execute("SELECT COUNT(*) FROM Accounts")
    count = int(db.cursor.fetchone()[0])
    if count == 0:
        # Show blocking modal to create Administrator
        def _after_created(email):
            print(f"[Setup] Admin created: {email}")

        AccountSetupDialog(window, force_admin=True, on_success=_after_created)
        # Modal is grab_set(), so code resumes when closed.
        # After creation, there will be at least 1 account.

def main():
    window = ttk.Window(title="Keai IWMS", themename="flatly", size=(1280, 720))
    ttk.window.Window.place_window_center(window)

    # If first run (no accounts), this will force-Admin creation
    _ensure_admin_gui(window)

    def onLogin(loginInstance: ttk.Frame, email: str) -> None:
        db = DatabaseConnection()
        employeeID = db.query_employee_login(email)
        if employeeID is None:
            # login frame should show its own error; do not destroy UI
            return

        loginInstance.destroy()
        lFrame = navigationFrame(window, employeeID, ttk.Frame())
        lFrame.getButtonCommand("Dashboard")
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1, minsize=200)
        window.columnconfigure(1, weight=20)

        # OPTIONAL: expose a way to add users later (e.g., from a menu or button)
        # Here's a tiny example that binds Ctrl+N to open the dialog:
        def _open_add_user(event=None):
            AccountSetupDialog(window, force_admin=False)
        window.bind("<Control-n>", _open_add_user)

    instance = Login(window, onLogin_callback=onLogin)
    window.mainloop()


if __name__ == "__main__":
    main()
