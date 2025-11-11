import ttkbootstrap as ttk
from Frames.Login import Login
from Frames.navigationFrame import navigationFrame
from utils_session import SessionTimeout
from ttkbootstrap.dialogs import Messagebox


def onLogin(login_view, user_ctx: dict):
    """
    user_ctx = {"employee_id": int, "email": str}
    登录成功后进入主系统界面，并启动 session timeout。
    """
    login_view.destroy()

    # 配置主窗口布局
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    # 右侧主内容区
    rFrame = ttk.Frame(window)
    rFrame.grid(row=0, column=1, sticky="nsew")
    rFrame.rowconfigure(0, weight=1)
    rFrame.columnconfigure(0, weight=1)

    # ===============================
    # 登出逻辑（手动或超时）
    # ===============================
    def do_logout():
        """销毁所有组件并返回登录界面"""
        try:
            if hasattr(window, "_session") and window._session:
                window._session.stop()
                window._session = None
        except Exception:
            pass

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

    # ===============================
    # 初始化导航栏 + Dashboard
    # ===============================
    emp_id = int(user_ctx["employee_id"])
    lFrame = navigationFrame(window, employeeID=emp_id, rFrame=rFrame, on_logout=do_logout)
    lFrame.getButtonCommand("Dashboard")

    # ===============================
    # 启动 Session Timeout 计时器（5分钟）
    # ===============================
    try:
        if hasattr(window, "_session") and window._session:
            window._session.stop()

        window._session = SessionTimeout(
            window,
            seconds=300,  # 5分钟无操作自动登出
            on_timeout=lambda: do_logout(),
            warn_title="Session Timeout"
        )
    except Exception as e:
        Messagebox.show_error(f"Failed to start session timer:\n{e}", "Error")


# ===============================
# 主程序入口
# ===============================
if __name__ == "__main__":
    window = ttk.window.Window(title="Keai IWMS", themename="flatly", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    # 初始化登录界面
    Login(window, onLogin_callback=onLogin)
    window.mainloop()
