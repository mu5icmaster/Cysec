import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, timezone
from Database.Database import DatabaseConnection

try:
    from zoneinfo import ZoneInfo     # Python 3.9+
    LOCAL_TZ = ZoneInfo("Asia/Kuala_Lumpur")
except Exception:
    # 退化：取系统本地时区（若没有 tzdata，可 pip install tzdata）
    LOCAL_TZ = datetime.now().astimezone().tzinfo


class LoggingFrame(ttk.Frame):
    """
    Admin-only: show system audit logs.
    Columns: Admin Name, Action, Target, Target ID, Time
    """
    def __init__(self, master: ttk.window.Window, role: str, employeeID: int):
        super().__init__(master, padding=10)
        self.role = role
        self.employeeID = employeeID
        self.db = DatabaseConnection()

        if str(self.role).lower() != "administrator":
            ttk.Label(self, text="Access denied.", bootstyle="danger").grid()
            return

        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.search_var = ttk.StringVar()
        ttk.Label(toolbar, text="Search").grid(row=0, column=0, padx=(0, 6))
        ttk.Entry(toolbar, textvariable=self.search_var, width=40).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(toolbar, text="Filter", bootstyle="secondary", command=self._filter).grid(row=0, column=2, padx=4)
        ttk.Button(toolbar, text="Refresh", bootstyle="info", command=self._refresh).grid(row=0, column=3, padx=4)

        # table
        cols = ("Admin Name", "Action", "Target", "Target ID", "Time")
        self.table = ttk.Treeview(self, columns=cols, show="headings", height=18)
        widths = [180, 160, 140, 120, 220]
        for c, w in zip(cols, widths):
            self.table.heading(c, text=c)
            self.table.column(c, width=w, anchor="w")
        self.table.grid(row=1, column=0, sticky="nsew")

        # 滚动条
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns")

        # 拉伸
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # 首次加载
        self._refresh()

    # ---------- 数据获取 ----------
    def _fetch_logs(self, limit: int = 500, keyword: str | None = None) -> list[tuple[str, str, str, str, str]]:
        """
        归一化返回 5 列： (actor_name, action, target_type, target_id, created_at)
        1) 优先调用 DatabaseConnection.logs_latest(limit)
           - 常见形状A: (id, actor_id, actor_name, action, target_type, target_id, detail, created_at)
           - 常见形状B: (actor_name, action, target_type, target_id, created_at)
           - 形状C:     (id, actor_name, action, target_type, target_id, created_at)
        2) 若无该方法，则直接 SELECT Logs 表（列名全小写）。
        """
        try:
            if hasattr(self.db, "logs_latest"):
                raw = self.db.logs_latest(limit)
                if keyword:
                    k = keyword.lower()
                    raw = [r for r in raw if k in " ".join(map(str, r)).lower()]

                norm: list[tuple[str, str, str, str, str]] = []
                for r in raw:
                    L = len(r)
                    if L >= 8:
                        # (id, actor_id, actor_name, action, target_type, target_id, detail, created_at)
                        actor_name = r[2]
                        action = r[3]
                        target_type = r[4]
                        target_id = r[5]
                        ts = r[7]
                    elif L == 6:
                        # (id, actor_name, action, target_type, target_id, created_at)
                        actor_name = r[1]
                        action = r[2]
                        target_type = r[3]
                        target_id = r[4]
                        ts = r[5]
                    elif L == 5:
                        # (actor_name, action, target_type, target_id, created_at)
                        actor_name, action, target_type, target_id, ts = r
                    else:
                        # 未知形状，跳过
                        continue

                    norm.append((str(actor_name), str(action), str(target_type), str(target_id), str(ts)))
                return norm

            # 无 logs_latest：直接查询 Logs
            conn = getattr(self.db, "conn", None) or getattr(self.db, "connection", None)
            cur = conn.cursor()
            if keyword:
                k = f"%{keyword}%"
                cur.execute(
                    """
                    SELECT actor_name, action, target_type, target_id, created_at
                    FROM Logs
                    WHERE actor_name LIKE ?
                       OR action LIKE ?
                       OR target_type LIKE ?
                       OR CAST(target_id AS TEXT) LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (k, k, k, k, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT actor_name, action, target_type, target_id, created_at
                    FROM Logs
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            data = cur.fetchall()
            cur.close()
            return [(str(r[0]), str(r[1]), str(r[2]), str(r[3]), str(r[4])) for r in data]

        except Exception as e:
            Messagebox.show_error(f"Failed to load logs:\n{e}", "Logging")
            return []

    # ---------- UI 刷新 ----------
    def _refresh(self):
        # 清空
        for i in self.table.get_children():
            self.table.delete(i)

        rows = self._fetch_logs(limit=500)
        for actor_name, action, target_type, target_id, ts in rows:
            ts_text = self._format_ts(ts)
            self.table.insert("", "end", values=(actor_name or "-", action, target_type, target_id, ts_text))

    def _filter(self):
        key = (self.search_var.get() or "").strip()
        for i in self.table.get_children():
            self.table.delete(i)

        rows = self._fetch_logs(limit=500, keyword=key if key else None)
        for actor_name, action, target_type, target_id, ts in rows:
            ts_text = self._format_ts(ts)
            self.table.insert("", "end", values=(actor_name or "-", action, target_type, target_id, ts_text))

    # ---------- 工具 ----------
    @staticmethod
    def _format_ts(ts: str) -> str:
        """
        统一把数据库里的时间转成本地可读时间。
        支持：epoch 秒/毫秒；ISO 字符串（有/无 Z）。
        所有“无时区”的时间都按 UTC 处理，再转 Asia/Kuala_Lumpur。
        """
        s = str(ts).strip()

    # 1) 纯数字：epoch（可能是秒，也可能是毫秒）
        if s.isdigit():
            t = int(s)
            if t > 1_000_000_000_000:   # 毫秒 -> 秒
                t //= 1000
            dt = datetime.fromtimestamp(t, tz=timezone.utc).astimezone(LOCAL_TZ)
            return dt.strftime("%Y-%m-%d %H:%M:%S")

    # 2) 文本：尝试 ISO 格式（'2025-11-11 13:02:03' / '2025-11-11T13:02:03Z'）
        try:
            s2 = s.replace("T", " ").replace("Z", "")  # 容错
            dt = datetime.fromisoformat(s2)
            if dt.tzinfo is None:                      # 无 tz -> 视为 UTC
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
        # 其它格式，原样返回
            return s

