import ttkbootstrap as ttk
from Frames.Login import Login
from Frames.navigationFrame import navigationFrame


def onLogin(login_view, user_ctx: dict):
    """
    user_ctx = {"employee_id": int, "email": str}
    """
    login_view.destroy()

    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    rFrame = ttk.Frame(window)
    rFrame.grid(row=0, column=1, sticky="nsew")
    rFrame.rowconfigure(0, weight=1)
    rFrame.columnconfigure(0, weight=1)

    def do_logout():
        for child in window.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        for c in range(3):
            try:
                window.columnconfigure(c, weight=0, minsize=0)
            except Exception:
                pass
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)
        Login(window, onLogin_callback=onLogin)

    emp_id = int(user_ctx["employee_id"])
    lFrame = navigationFrame(window, employeeID=emp_id, rFrame=rFrame, on_logout=do_logout)
    lFrame.getButtonCommand("Dashboard")


if __name__ == "__main__":
    window = ttk.window.Window(title="Keai IWMS", themename="flatly", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    Login(window, onLogin_callback=onLogin)
    window.mainloop()
