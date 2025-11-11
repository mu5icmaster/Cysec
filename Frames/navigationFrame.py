import re
import ttkbootstrap as ttk
from PIL import ImageTk, Image, ImageDraw

from utils import fonts
from Database import Database
from configuration import Configuration

from Frames.productFrame import productFrame
from Frames.inventoryFrame import inventoryFrame
from Frames.purchaseOrderFrame import purchaseOrderFrame
from Frames.salesOrderFrame import salesOrderFrame
from Frames.taskFrame import taskFrame
from Frames.vendorFrame import vendorFrame
from Frames.settingsPopup import SettingsPopup
from Frames.dashboardFrame import DashboardFrame
from Frames.reportsFrame import ReportFrame
from Frames.accountSetupDialog import AccountSetupDialog
from Frames.loggingFrame import LoggingFrame 



class navigationFrame(ttk.Frame):
    """
    Left navigation + header. Pages mount in self.content_container.
    Role is resolved by exact join:
      Workers(RoleID) -> Roles(RoleID) using Workers.WorkerID
    """

    def __init__(self, master: ttk.window.Window, employeeID: int, rFrame: ttk.Frame, on_logout=None) -> None:
        self.Fonts = fonts()
        self.styleObj = master.style
        self.config = Configuration()
        self.master = master
        self.content_container = rFrame
        self.db = Database.DatabaseConnection()
        self.employeeID = int(employeeID)
        self.on_logout = on_logout

        # ---- Exact schema lookups (NO guesses) ----
        self.name = self._get_name_by_worker_id(self.employeeID) or "User"
        self.role = self._get_role_name_by_worker_id(self.employeeID) or "Worker"

        # Menu by role name from Roles table
        buttonConfig = {
            "Worker": ["Dashboard", "Inventory", "Report", "Tasks"],
            "Supervisor": ["Dashboard", "Product", "Inventory", "Purchase Order", "Sales Order", "Tasks", "Vendor", "Report"],
            "Administrator": ["Dashboard", "Product", "Inventory", "Purchase Order", "Sales Order", "Vendor", "Report", "Add Worker", "Logging"]
        }
        if self.role not in buttonConfig:
            self.role = "Worker"

        # Theme
        prefs = self.config.getPreferences(str(self.employeeID))
        self.styleObj.theme_use(prefs[1])

        # Frame
        super().__init__(master, bootstyle="warning")
        self.grid(row=0, column=0, sticky="nwes")

        # Images
        graphicsPath = self.config.getGraphicsPath()
        self.images = [
            Image.open(f"{graphicsPath}/settingsIcon.png").resize((40, 40)),
            self.make_circular_image(f"{graphicsPath}/User_Avatars/{prefs[0]}.png", 200),
        ]
        self.imageObject = [ImageTk.PhotoImage(im) for im in self.images]

        # Layout
        northFrame = ttk.Frame(self, bootstyle="warning", padding=20)
        southFrame = ttk.Frame(self, bootstyle="warning", padding=20)
        northFrame.grid(row=0, column=0, sticky="nwes")
        southFrame.grid(row=1, column=0, sticky="nwes")
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=1)

        # Header
        ttk.Label(northFrame, text="KEAI", font=self.Fonts.fonts["header3"],
                  bootstyle="warning-inverse", foreground="black").grid(row=1, column=1, sticky="nw")
        ttk.Button(northFrame, image=self.imageObject[0], bootstyle="warning",
                   command=lambda: SettingsPopup(self.master, self.employeeID, self.redisplay_theme))\
            .grid(row=1, column=3, sticky="ne")
        ttk.Label(northFrame, image=self.imageObject[1], bootstyle="warning-inverse")\
            .grid(row=2, column=1, sticky="nws")
        userFrame = ttk.Frame(northFrame, bootstyle="warning")
        userFrame.grid(row=2, column=2, columnspan=2, sticky="nwes")
        ttk.Label(userFrame, text=self.name, font=self.Fonts.fonts["regular2"],
                  bootstyle="warning-inverse", foreground="black", anchor=ttk.CENTER)\
            .grid(row=1, column=1, sticky="swe")
        ttk.Label(userFrame, text=str(self.role), font=self.Fonts.fonts["regular2"],
                  bootstyle="warning-inverse", foreground="black", anchor=ttk.CENTER)\
            .grid(row=2, column=1, sticky="nwe")

        # Menu
        self.styleObj.configure(style="dark.Link.TButton",
                                font=self.Fonts.get_font("regular2"),
                                foreground="black")
        for row, text in enumerate(buttonConfig[self.role], start=1):
            ttk.Button(southFrame, text=text, bootstyle="dark-link",
                       command=lambda x=text: self.getButtonCommand(x))\
                .grid(row=row, column=1, sticky="we")
            southFrame.rowconfigure(row, weight=1)

        # Logout
        last_row = len(buttonConfig[self.role]) + 1
        ttk.Separator(southFrame, orient="horizontal").grid(row=last_row, column=1, sticky="ew", pady=(8, 4))
        ttk.Button(southFrame, text="Logout", bootstyle="danger-link",
                   command=(self.on_logout if self.on_logout else self.master.destroy))\
            .grid(row=last_row + 1, column=1, sticky="we")
        southFrame.columnconfigure(1, weight=1)

        # Right container stretch
        self.content_container.grid_propagate(True)
        self.content_container.rowconfigure(0, weight=1)
        self.content_container.columnconfigure(0, weight=1)

    # ---------- Exact DB lookups for your schema ----------

    def _conn(self):
        return getattr(self.db, "conn", None) or getattr(self.db, "connection", None)

    def _get_name_by_worker_id(self, worker_id: int):
        """
        Workers(WorkerID, RoleID, Name, ContactNumber)
        """
        conn = self._conn()
        if conn is None:
            return None
        cur = conn.cursor()
        try:
            cur.execute("SELECT Name FROM Workers WHERE WorkerID = ?", (worker_id,))
            row = cur.fetchone()
            return str(row[0]) if row and row[0] is not None else None
        except Exception:
            return None
        finally:
            cur.close()

    def _get_role_name_by_worker_id(self, worker_id: int):
        """
        JOIN: Workers(RoleID) -> Roles(RoleID) to get Roles.RoleName
        """
        conn = self._conn()
        if conn is None:
            return None
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT r.RoleName
                FROM Workers w
                JOIN Roles r ON w.RoleID = r.RoleID
                WHERE w.WorkerID = ?
            """, (worker_id,))
            row = cur.fetchone()
            return str(row[0]) if row and row[0] is not None else None
        except Exception:
            return None
        finally:
            cur.close()

    # ---------- Page mounting ----------

    def _clear_content(self):
        for child in self.content_container.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

    def _show_page(self, page_cls):
        self._clear_content()
        page = page_cls(self.content_container, self.role, self.employeeID)
        try:
            page.grid(row=0, column=0, sticky="nsew")
        except Exception:
            pass

    def getButtonCommand(self, text):
        mapping = {
            "Dashboard": DashboardFrame,
            "Product": productFrame,
            "Inventory": inventoryFrame,
            "Purchase Order": purchaseOrderFrame,
            "Sales Order": salesOrderFrame,
            "Tasks": taskFrame,
            "Vendor": vendorFrame,
            "Report": ReportFrame,
            "Logging": LoggingFrame
        }
        if text in mapping:
            self._show_page(mapping[text])
        elif text == "Add Worker":
            AccountSetupDialog(
                self.master,
                force_admin=(self.role == "Administrator"),
                fixed_role=None,
                on_success=lambda email: None
            )

    def redisplay_theme(self):
        current_cls = None
        if self.content_container.winfo_children():
            current_cls = type(self.content_container.winfo_children()[0])
        self.destroy()
        new = navigationFrame(self.master, self.employeeID, self.content_container, on_logout=self.on_logout)
        if current_cls is not None:
            new._show_page(current_cls)

    def make_circular_image(self, image_path, output_diameter):
        img = Image.open(image_path).resize((output_diameter, output_diameter))
        mask = Image.new('L', (output_diameter, output_diameter), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, output_diameter, output_diameter), fill=255)
        output_img = Image.new(img.mode, (output_diameter, output_diameter), 0)
        output_img.paste(img, mask=mask)
        radius = int(output_diameter / 2)
        return output_img.resize((radius, radius))
