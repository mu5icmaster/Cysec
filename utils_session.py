# utils_session.py
import time
from ttkbootstrap.dialogs import Messagebox

class SessionTimeout:
    def __init__(self, root, seconds=300, on_timeout=None, warn_title="Session Timeout"):
        self.root = root
        self.seconds = int(seconds)
        self.on_timeout = on_timeout
        self.warn_title = warn_title
        self._last = time.time()
        self._job = None

        # 绑定“用户活动”事件（尽量轻量）
        for ev in ("<Key>", "<Button>", "<MouseWheel>"):
            root.bind_all(ev, self._mark_activity, add="+")
        # 如果你愿意也可以加 "<Motion>"，但它事件很频繁
        # root.bind_all("<Motion>", self._mark_activity, add="+")

        self._tick()

    def _mark_activity(self, _=None):
        self._last = time.time()

    def _tick(self):
        if time.time() - self._last >= self.seconds:
            try:
                Messagebox.show_warning(
                    "You’ve been signed out due to 5 minutes of inactivity.",
                    self.warn_title,
                    parent=self.root
                )
            except Exception:
                pass
            if callable(self.on_timeout):
                self.on_timeout()
            return
        self._job = self.root.after(1000, self._tick)

    def reset_now(self):
        self._last = time.time()

    def stop(self):
        if self._job:
            try:
                self.root.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
