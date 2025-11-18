import ttkbootstrap as ttk
from ttkbootstrap.validation import validator, add_validation
import os
import re
from datetime import datetime, timedelta
import calendar
import webbrowser
import random

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.colors import green, orange, red, black
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.platypus as platypus

from Frames.pageFrame import pageFrame
from Database import DatabaseConnection
from utils import previewText


class ReportFrame(pageFrame):
    def __init__(self, master: ttk.window.Window, role: str, employee_id: int):
        # Inherits Page Frame
        super().__init__(master=master,
                         title="Reports",
                         role=role,
                         button_config={
                             "Worker": ["Product Movement", "Stock Level"],
                             "Supervisor": [
                                 "Product Movement", "Stock Level",
                                 "Performance Report", "Traceability Report",
                                 "User Activities"
                             ],
                             "Administrator": [
                                 "Product Movement", "Stock Level",
                                 "Performance Report", "Traceability Report",
                                 "User Activities"
                             ]
                         },
                         employeeID=employee_id)

        self.db_connection = DatabaseConnection()

        # cache for user activities + filter UI handle
        self._ua_all_rows = None
        self._ua_filter_frame: ttk.Frame | None = None
        self._ua_filter_var = ttk.StringVar(value="All")

        self.product_movement_report()

    # --------------------------------
    # Report switchers
    # --------------------------------
    def product_movement_report(self):
        self._destroy_ua_filter()
        column_names = ("Date", "Product", "Batch No.", "From", "To", "Quantity", "Status")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_product_movement_report())

    def stock_level_report(self):
        self._destroy_ua_filter()
        column_names = ("Product", "Unit Cost", "Total Value", "On Hand", "Free to Use", "Incoming", "Outgoing")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_stock_level_report())

    def performance_report(self):
        self._destroy_ua_filter()
        selected = self._dialog_employee()
        if not selected:
            return
        # expected 'ID - Name'
        employee_id = selected.split(' - ')[0].strip()
        try:
            parameters = [value for value in self.db_connection.query_employee_report(employee_id)]
        except Exception as e:
            ttk.Messagebox.show_error(f"Could not load report for {selected}.\n\n{e}")
            return

        image = f"{self.config.getGraphicsPath()}/User_Avatars/{self.config.getPreferences(employee_id)[0]}.png"
        self._generate_report(parameters + [image])


    def traceability_report(self):
        self._destroy_ua_filter()
        batch_number = self._dialog_product_batch_no()
        if batch_number is None:
            return
        batch_number = (batch_number.split(' - ')[0], batch_number.split(' - ')[1])
        column_names = ("PIC", "Product Name", "Date", "Batch No.", "From", "To", "Quantity")
        self._insert_table_headings(column_names)
        self._load_table_rows(self.db_connection.query_traceability_report(batch_number[0], batch_number[1]))

    def user_activities_report(self):
        """
        Show User Activities report. Falls back to local dummy data if no DB or no rows exist.
        """
        import random
        from datetime import datetime, timedelta

        # --- 1️⃣ Build headings first ---
        column_names = ("Date", "Time", "User", "Activity", "Remark")
        self._insert_table_headings(column_names)

        # --- 2️⃣ Try to fetch from DB ---
        try:
            data = self.db_connection.query_user_activities_report()
        except Exception as e:
            print("DB query failed, using dummy data instead:", e)
            data = []

        # --- 3️⃣ If empty or connection fails, build local dummy dataset ---
        if not data or len(data) == 0:
            fake_users = [
                ("Admin One", "Administrator"),
                ("Supervisor Sam", "Supervisor"),
                ("Worker Wendy", "Worker"),
                ("Worker Will", "Worker"),
                ("Worker Wren", "Worker"),
            ]
            fake_actions = [
                "Login", "Logout", "Added Product", "Updated Inventory",
                "Generated Report", "Reviewed Task", "Added Vendor",
                "Deleted Product", "Approved Order", "Adjusted Stock"
            ]
            fake_remarks = ["Success", "Failed", "No issues", "Check later",
                            "Auto-generated", "Manual override", "Approved", "Rejected"]

            today = datetime.now().date()
            data = []
            for _ in range(60):
                d = today - timedelta(days=random.randint(0, 60))
                t = f"{random.randint(0,23):02}:{random.randint(0,59):02}:{random.randint(0,59):02}"
                user = random.choice(fake_users)
                data.append((
                    str(d),
                    t,
                    f"{user[0]} ({user[1]})",
                    random.choice(fake_actions),
                    random.choice(fake_remarks)
                ))

        # --- 4️⃣ Save for filtering, show filter bar and render ---
        self._ua_all_rows = data
        self._build_ua_filter_bar()
        self._apply_ua_filter_and_render()

    # --------------------------------
    # Demo data bootstrap
    # --------------------------------
    def _ensure_demo_data(self):
        """
        Safely ensure minimal tables + seed roles/users/logs if empty.
        Won't overwrite existing data; designed to be no-op on a live DB.
        """
        conn = getattr(self.db_connection, "conn", None)
        if conn is None:
            return  # no connection object exposed; skip
        cur = conn.cursor()
        try:
            # 1) Minimal schemas (adjust names/types if you have stricter schema)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Roles (
                    RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
                    RoleName TEXT UNIQUE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Workers (
                    WorkerID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    RoleID INTEGER NOT NULL,
                    Email TEXT,
                    ContactNumber TEXT,
                    FOREIGN KEY(RoleID) REFERENCES Roles(RoleID)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Logs (
                    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date TEXT NOT NULL,
                    Time TEXT NOT NULL,
                    WorkerID INTEGER,
                    Activity TEXT NOT NULL,
                    Remark TEXT,
                    FOREIGN KEY(WorkerID) REFERENCES Workers(WorkerID)
                )
            """)
            conn.commit()

            # 2) Seed roles if empty
            cur.execute("SELECT COUNT(*) FROM Roles")
            if (cur.fetchone() or [0])[0] == 0:
                cur.executemany("INSERT INTO Roles (RoleName) VALUES (?)",
                                [("Administrator",), ("Supervisor",), ("Worker",)])
                conn.commit()

            # 3) Seed workers if empty
            cur.execute("SELECT COUNT(*) FROM Workers")
            if (cur.fetchone() or [0])[0] == 0:
                # get role ids
                cur.execute("SELECT RoleID, RoleName FROM Roles")
                role_map = {name: rid for rid, name in cur.fetchall()}
                dummy_users = [
                    ("Admin One", role_map.get("Administrator", 1), "admin@demo.com", "09170000001"),
                    ("Supervisor Sam", role_map.get("Supervisor", 2), "sam@demo.com", "09170000002"),
                    ("Worker Wendy", role_map.get("Worker", 3), "wendy@demo.com", "09170000003"),
                    ("Worker Will", role_map.get("Worker", 3), "will@demo.com", "09170000004"),
                    ("Worker Wren", role_map.get("Worker", 3), "wren@demo.com", "09170000005"),
                ]
                cur.executemany("""
                    INSERT INTO Workers (Name, RoleID, Email, ContactNumber)
                    VALUES (?, ?, ?, ?)
                """, dummy_users)
                conn.commit()

            # 4) Seed logs if empty
            cur.execute("SELECT COUNT(*) FROM Logs")
            if (cur.fetchone() or [0])[0] == 0:
                cur.execute("SELECT WorkerID, Name FROM Workers")
                workers = cur.fetchall()
                actions = [
                    "Login", "Logout", "Created Order", "Updated Inventory",
                    "Generated Report", "Reviewed Task", "Added Vendor",
                    "Deleted Product", "Adjusted Stock", "Approved Order"
                ]
                remarks = ["Success", "Failure", "No Issues", "Manual Override", "Auto Entry", "Approved", "Rejected"]

                today = datetime.now().date()
                dummy_logs = []
                for _ in range(100):
                    worker = random.choice(workers)
                    d = today - timedelta(days=random.randint(0, 60))
                    t = f"{random.randint(0,23):02}:{random.randint(0,59):02}:{random.randint(0,59):02}"
                    dummy_logs.append((
                        str(d), t, worker[0], random.choice(actions), random.choice(remarks)
                    ))

                cur.executemany("""
                    INSERT INTO Logs (Date, Time, WorkerID, Activity, Remark)
                    VALUES (?, ?, ?, ?, ?)
                """, dummy_logs)
                conn.commit()

        except Exception as e:
            # Keep UI resilient; just print for dev
            print("Demo bootstrap error:", e)
            conn.rollback()
        finally:
            cur.close()

    # --------------------------------
    # Filter bar for User Activities
    # --------------------------------
    def _build_ua_filter_bar(self):
        # Parent is the same bottom frame that holds the table
        bottom_frame = self.tableview.master

        # If we already have one, destroy and rebuild (resets layout cleanly)
        self._destroy_ua_filter()

        self._ua_filter_frame = ttk.Frame(bottom_frame, padding=(12, 8))
        # Place above the table (row 0); table itself is row 1 in pageFrame
        self._ua_filter_frame.grid(row=0, column=1, sticky="ew")
        bottom_frame.columnconfigure(1, weight=1)

        ttk.Label(self._ua_filter_frame, text="Filter:", font=self.font.get_font("regular2")).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )

        combo = ttk.Combobox(
            self._ua_filter_frame,
            textvariable=self._ua_filter_var,
            values=["All", "Today", "Last 7 days", "Last 30 days", "This Month", "This Year"],
            state="readonly",
            width=16,
        )
        combo.grid(row=0, column=1, sticky="w")
        combo.bind("<<ComboboxSelected>>", lambda e: self._apply_ua_filter_and_render())

        ttk.Button(self._ua_filter_frame, text="Refresh", bootstyle="secondary",
                   command=self._refresh_ua_data).grid(row=0, column=2, padx=(8, 0))

        # little spacer
        ttk.Separator(self._ua_filter_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )

        self._ua_filter_frame.columnconfigure(0, weight=0)
        self._ua_filter_frame.columnconfigure(1, weight=0)
        self._ua_filter_frame.columnconfigure(2, weight=1)

    def _destroy_ua_filter(self):
        if self._ua_filter_frame is not None and self._ua_filter_frame.winfo_exists():
            try:
                self._ua_filter_frame.destroy()
            except Exception:
                pass
        self._ua_filter_frame = None

    def _refresh_ua_data(self):
        """Requery DB and reapply active filter."""
        try:
            self._ua_all_rows = self.db_connection.query_user_activities_report()
        except Exception as e:
            print("Refresh query failed:", e)
            self._ua_all_rows = []
        self._apply_ua_filter_and_render()

    def _apply_ua_filter_and_render(self):
        if not self._ua_all_rows:
            self.tableview.delete_rows()
            self.tableview.load_table_data()
            return

        key = (self._ua_filter_var.get() or "All").strip()

        # Compute date window
        start, end = self._date_window_for_key(key)  # both are datetime.date or None
        rows = []
        for row in self._ua_all_rows:
            # Expecting ("YYYY-MM-DD", "HH:MM:SS", user, activity, remark)
            raw_date = str(row[0]) if len(row) > 0 else ""
            dt = self._safe_parse_date(raw_date)
            if start and end and dt:
                if start <= dt <= end:
                    rows.append(row)
            else:
                # no filter or failed to parse -> include for "All"
                if start is None and end is None:
                    rows.append(row)

        self._load_table_rows(rows)

    def _safe_parse_date(self, s: str):
        """Try a few common formats, return date() or None."""
        fmts = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
        for f in fmts:
            try:
                return datetime.strptime(s, f).date()
            except Exception:
                continue
        # last resort: try to slice first 10 chars if ISO-like
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").date()
        except Exception:
            return None

    def _date_window_for_key(self, key: str):
        """Return (start_date, end_date) inclusive for filter key."""
        today = datetime.now().date()

        if key == "All":
            return (None, None)
        if key == "Today":
            return (today, today)
        if key == "Last 7 days":
            return (today - timedelta(days=6), today)
        if key == "Last 30 days":
            return (today - timedelta(days=29), today)
        if key == "This Month":
            start = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end = today.replace(day=last_day)
            return (start, end)
        if key == "This Year":
            start = today.replace(month=1, day=1)
            end = today.replace(month=12, day=31)
            return (start, end)

        # default: no filter
        return (None, None)

    # --------------------------------
    # UI plumbing
    # --------------------------------
    def _insert_table_headings(self, column_names: tuple) -> None:
        self.tableview.purge_table_data()
        for column in column_names:
            self._insert_table_columns(column)

    def getButtonCommand(self, button_text):
        if button_text == "Product Movement":
            self.product_movement_report()
        elif button_text == "Stock Level":
            self.stock_level_report()
        elif button_text == "Performance Report":
            self.performance_report()
        elif button_text == "Traceability Report":
            self.traceability_report()
        elif button_text == "User Activities":
            self.user_activities_report()

    # --------------------------------
    # Dialogs
    # --------------------------------
    def _dialog_employee(self) -> str | None:
        """
        Admin/Supervisor can select an employee from a read-only dropdown populated
        with people already in the system (Workers table).
        Returns the selected string (e.g., '12 - Jane Doe') or None if cancelled.
        """
        # Only allow Admin/Supervisor to pick
        if self.role not in ("Administrator", "Supervisor"):
            ttk.Messagebox.show_warning("You don’t have permission to run Performance Report.")
            return None

        values = self._list_employees_for_picker()

        toplevel = ttk.Toplevel(master=self.master, width=420, height=160, resizable=(False, False),
                                title="Performance Report", transient=self.master, minsize=(420, 160))
        toplevel.selected_employee = None

        ttk.Frame(toplevel, height=16).grid(row=0, column=0)
        ttk.Label(toplevel, text="Enter Employee Name", font=self.font.get_font("thin2"),
                anchor=ttk.W).grid(row=1, column=0, sticky="nwes", padx=20)

        entry = ttk.Combobox(toplevel, values=values, state="readonly")
        entry.grid(row=2, column=0, sticky="nwes", padx=20)
        if values:
            entry.set(values[0])  # default to first employee

        ttk.Separator(toplevel).grid(row=3, column=0, columnspan=3, sticky="wes", pady=(8, 0))
        btn_row = ttk.Frame(toplevel, padding=10)
        btn_row.grid(row=4, column=0, sticky="nwes")

        def on_submit():
            sel = entry.get()
            if sel and sel in values:
                toplevel.selected_employee = sel
                toplevel.destroy()
            else:
                # Shouldn't happen with readonly, but guard anyway
                ttk.Label(btn_row, text="Please pick a name from the list.",
                        bootstyle="danger", anchor=ttk.CENTER,
                        font=self.font.get_font("error")).grid(row=2, column=1, columnspan=2, sticky="we")

        ttk.Button(btn_row, text="Cancel", bootstyle="danger",
                command=lambda: toplevel.destroy()).grid(row=1, column=1, padx=(0, 6))
        ttk.Button(btn_row, text="Submit", bootstyle="success",
                command=on_submit).grid(row=1, column=2)

        # layout weights
        toplevel.rowconfigure(2, weight=1)
        toplevel.columnconfigure(0, weight=1)
        btn_row.columnconfigure(0, weight=8)
        btn_row.columnconfigure(1, weight=1)
        btn_row.columnconfigure(2, weight=1)

        toplevel.wait_window()
        return toplevel.selected_employee

    def _list_employees_for_picker(self) -> list[str]:
        """
        Returns values formatted as 'WorkerID - Name' for the combobox.
        Falls back to [] if nothing is available.
        """
        try:
            vals = self.db_connection.query_worker()  # expected to already be ['1 - Alice', '2 - Bob', ...]
            if not vals:
                return []
            # Normalize to strings and ensure the ' - ' format
            out = []
            for v in vals:
                if isinstance(v, (tuple, list)) and len(v) >= 2:
                    out.append(f"{v[0]} - {v[1]}")
                else:
                    s = str(v)
                    out.append(s if " - " in s else s)  # keep as-is if already 'ID - Name'
            return out
        except Exception:
            return []


    def _dialog_product_batch_no(self) -> str | None:
        def on_submit_button():
            text = entry.get()
            if text in entry.cget("values"):
                toplevel.destroy()
                toplevel.selected_batch_no = text
            else:
                ttk.Label(frame, text="Submission failed to process", bootstyle="danger",
                          anchor=ttk.CENTER, font=self.font.get_font("error"))\
                    .grid(row=2, column=1, columnspan=2, sticky="we")

        toplevel = ttk.Toplevel(master=self.master, width=400, height=150, resizable=(False, False),
                                title="Traceability Report", transient=self.master, minsize=(400, 150))
        errVar = ttk.StringVar()
        toplevel.selected_batch_no = None

        ttk.Frame(toplevel, height=20).grid(row=0, column=0)
        ttk.Label(toplevel, text="Enter Batch No.", font=self.font.get_font("thin2"),
                  anchor=ttk.W).grid(row=1, column=0, sticky="nwes", padx=20)
        entry = ttk.Combobox(toplevel, values=self.db_connection.query_productBatchNo())
        entry.grid(row=2, column=0, sticky="nwes", padx=20)
        ttk.Label(toplevel, textvariable=errVar, anchor=ttk.NW, font=self.font.get_font("error"),
                  foreground=self.styleObj.colors.get("danger")).grid(row=3, column=0, sticky="nwes", padx=20)
        ttk.Separator(toplevel).grid(row=4, column=0, columnspan=3, sticky="wes")
        frame = ttk.Frame(toplevel, padding=10)
        frame.grid(row=5, column=0, sticky="nwes")

        toplevel.rowconfigure(0, weight=0)
        toplevel.rowconfigure(1, weight=0)
        toplevel.rowconfigure(2, weight=1)
        toplevel.rowconfigure(3, weight=1)
        toplevel.rowconfigure(4, weight=1)
        toplevel.rowconfigure(5, weight=0)
        toplevel.columnconfigure(0, weight=1)

        ttk.Button(frame, text="Cancel", bootstyle="danger",
                   command=lambda: toplevel.destroy()).grid(row=1, column=1)
        ttk.Button(frame, text="Submit", bootstyle="success",
                   command=lambda: on_submit_button()).grid(row=1, column=2)

        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=8)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        # Preview Text
        previewText(entry, key="batchNoEntry")

        # Validation
        def validate_entry(event):
            if event.postchangetext in event.widget.cget("values") or event.postchangetext == "":
                errVar.set("")
                return True
            else:
                errVar.set("Invalid Batch No.")
                return False

        add_validation(entry, validator(validate_entry), when="focus")
        toplevel.wait_window()
        return toplevel.selected_batch_no

    # --------------------------------
    # PDF generation for Performance
    # --------------------------------
    def _generate_report(self, parameters: list[str]):
        """Parameters: [Employee ID - Employee Name, Employee Role, Email, Contact Number,
        Tasks Assigned, Tasks Completed, Tasks Overdue, PFP Image Path]"""
        report_files = [f for f in os.listdir(self.config.getReportsFile()) if re.match(r"Report_\d+.pdf", f)]

        if report_files:
            report_files.sort(key=lambda f: int(re.search(r'\d+', f).group()))
            last_file = report_files[-1]
            file_number = int(re.search(r"\d+", last_file).group())
            file_name = f"{self.config.getReportsFile()}/Report_{file_number + 1}.pdf"
        else:
            file_name = f"{self.config.getReportsFile()}/Report_1.pdf"

        self.__create_pdf__(file_name, parameters)
        webbrowser.open_new(f'file://{file_name}')

    def __create_pdf__(self, output_filename: str, parameters: list[str]):
        c = canvas.Canvas(output_filename, pagesize=A5)

        # Title
        title = "Worker Performance Report"
        pdfmetrics.registerFont(TTFont('Lexend', f'{self.config.repo_file_path}/Fonts/Lexend-Regular.ttf'))
        c.setFont('Lexend', 16)
        c.setFillColor(black)
        title_width = pdfmetrics.stringWidth(title, 'Lexend', 16)
        title_x = (420 - title_width) / 2
        title_y = 520
        c.drawString(title_x, title_y, title)

        # Subtitle
        subtitle = f"Report generated on {datetime.now().strftime('%d %B %Y, %A')}"
        c.setFont('Lexend', 10)
        subtitle_width = pdfmetrics.stringWidth(subtitle, 'Lexend', 10)
        subtitle_x = (420 - subtitle_width) / 2
        subtitle_y = 500
        c.drawString(subtitle_x, subtitle_y, subtitle)

        subtitle_part2 = f"For employee {parameters[0].split(' - ')[1]}"
        subtitle_width2 = pdfmetrics.stringWidth(subtitle_part2, 'Lexend', 10)
        subtitle_x2 = (420 - subtitle_width2) / 2
        subtitle_y2 = 485
        c.drawString(subtitle_x2, subtitle_y2, subtitle_part2)

        # PFP
        image = platypus.Image(parameters[7], width=100, height=100)
        image.drawOn(c, 50, 300)

        # Employee info
        text_objects = parameters[:4]
        for i, text in enumerate(text_objects):
            text_width = pdfmetrics.stringWidth(text, 'Lexend', 12)
            x = 100 - text_width / 2
            c.setFont('Lexend', 12)
            c.drawString(x, 250 - i * 30, text)

        # Meter text
        tasks_completed_text = f"Tasks completed: {parameters[5]}/{parameters[4]}"
        c.setFont('Lexend', 12)
        tasks_completed_text_width = pdfmetrics.stringWidth(tasks_completed_text, 'Lexend', 12)
        tasks_completed_text_x = (550 - tasks_completed_text_width) / 2
        tasks_completed_text_y = 350
        c.drawString(tasks_completed_text_x, tasks_completed_text_y, tasks_completed_text)

        # Meter
        tasks_assigned = parameters[4]
        tasks_completed = parameters[5]
        completion_rate = int(tasks_completed) / int(tasks_assigned) if tasks_assigned else 0
        color = green if completion_rate > 0.8 else orange if completion_rate > 0.5 else red

        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setFillColorRGB(0.7, 0.7, 0.7)
        c.circle(275, 265, 50, fill=1)

        c.setStrokeColor(color)
        c.setFillColor(color)
        c.wedge(225, 215, 325, 315, 90, completion_rate * 360 if completion_rate else 1, fill=1)

        c.setStrokeColorRGB(1, 1, 1)
        c.setFillColorRGB(1, 1, 1)
        c.circle(275, 265, 30, fill=1)

        text_part2 = f"{completion_rate * 100:.1f}%"
        text_width2 = pdfmetrics.stringWidth(text_part2, 'Lexend', 12)
        x2 = 277 - text_width2 / 2
        y2 = 261
        c.setFillColor('black')
        c.drawString(x2, y2, text_part2)

        c.setFont('Lexend', 12)
        c.drawString(200, 170, f"Task Completion Rate: {completion_rate * 100:.1f}%")

        c.setFont('Lexend', 8)
        footer_text = f"Page 1 | Generated on {datetime.now().strftime('%d %B %Y, %A')}"
        footer_width = pdfmetrics.stringWidth(footer_text, 'Lexend', 8)
        footer_x = (420 - footer_width) / 2
        footer_y = 20
        c.drawString(footer_x, footer_y, footer_text)

        new_row_text = "Reports are saved to (repository_path)/Reports by default"
        new_row_width = pdfmetrics.stringWidth(new_row_text, 'Lexend', 8)
        new_row_x = (420 - new_row_width) / 2
        new_row_y = 10
        c.drawString(new_row_x, new_row_y, new_row_text)

        c.save()


if __name__ == '__main__':
    from navigationFrame import navigationFrame

    # Create Main Window, and center it
    window = ttk.Window(title="Keai IWMS", themename="litera", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    # Creates Frames
    lFrame = navigationFrame(window, 1, ttk.Frame(window))
    lFrame.getButtonCommand("Report")
    lFrame.rFrame.user_activities_report()

    # Starts Event Main Loop
    window.mainloop()
