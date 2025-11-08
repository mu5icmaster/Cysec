from PIL import Image
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from utils import fonts
from configuration import Configuration
from Database.Database import DatabaseConnection

from Frames.notificationFrame import notificationFrame

# DO NOT REMOVE - alias for Image.Cubic which is deprecated for PIL > 10.0.0, used in ttk.Meter
Image.CUBIC = Image.BICUBIC


class DashboardFrame(ttk.Frame):
    def __init__(self, master: ttk.window.Window, role: str, employeeID: int):
        # Inherit ttk.Frame
        super().__init__(master)
        self.grid(row=0, column=1, sticky="nwes")

        # Create references
        self.masterWindow = master
        self.employeeID = employeeID
        self.role = role
        self.styleObj = ttk.style.Style.get_instance()
        self.font = fonts()
        self.config = Configuration()
        self.db_connection = DatabaseConnection()
        graphics_path = self.config.getGraphicsPath()
        self.images = [
            Image.open(f'{graphics_path}/notificationIcon.png').resize((50, 50))
        ]
        self.imageObject = []
        for im in self.images:
            self.imageObject += [ImageTk.PhotoImage(image=im)]

        # Create Vertical Frames
        top_frame = ttk.Frame(self)
        top_frame.grid(row=1, column=1, sticky="nwes")

        middle_frame = ttk.Frame(self, bootstyle="light")
        middle_frame.grid(row=2, column=1, sticky="nwes")

        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.grid(row=3, column=1, sticky="nwes")

        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=16)
        self.columnconfigure(1, weight=1)

        # Top Frame Widgets
        dashboard_label = ttk.Label(top_frame, text="Dashboard", font=self.font.fonts["header3"])
        self.styleObj.configure(style="light.TButton", background="white", borderwidth=0)
        notificationButton = ttk.Button(top_frame, image=self.imageObject[0], bootstyle="light",
                                        command=lambda: notificationFrame(self.masterWindow, self.employeeID))
        dashboard_label.grid(row=1, column=1, sticky="nw", padx=20, pady=20)
        notificationButton.grid(row=1, column=2, sticky="nes")

        top_frame.rowconfigure(1, weight=1)
        top_frame.rowconfigure(2, weight=3)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=0)

        # Configure Middle Frame and Bottom Frame
        self.configure_middle_frame(middle_frame)
        self.configure_bottom_frame(bottom_frame)

    def configure_middle_frame(self, middle_frame: ttk.Frame):
        # Create Frames
        left_frame = ttk.Frame(middle_frame, bootstyle="light", padding=10)
        left_frame.grid(row=1, column=1, sticky="nwes")

        right_frame = ttk.Frame(middle_frame, bootstyle="light", padding=10)
        right_frame.grid(row=1, column=2, sticky="nwes")

        middle_frame.rowconfigure(1, weight=1)
        middle_frame.columnconfigure(1, weight=3)
        middle_frame.columnconfigure(2, weight=1)

        # Left Frame
        ttk.Label(left_frame, text="Sales Activity", font=self.font.get_font("regular4"), foreground="black",
                  bootstyle="inverse-light").grid(row=0, column=0, columnspan= 4, sticky="nw", pady=4, padx=4)
        self._info_frame(left_frame, column=0, qty=len(self.db_connection.query_SalesOrder()),
                         qty_style="info", info="Sales Order Created")
        self._info_frame(left_frame, column=1, qty=len(self.db_connection.query_updatableSalesOrder()),
                         qty_style="danger", info="Sales Order Pending")
        self._info_frame(left_frame, column=2, qty=len(self.db_connection.query_salesOrder_delivered()),
                         qty_style="success", info="Sales Order Delivered")
        self._info_frame(left_frame, column=3, qty=self.db_connection.query_stock_sold(),
                         qty_style="success", info="Stock Sold")

        left_frame.rowconfigure(0, weight=0)
        left_frame.rowconfigure(1, weight=0)
        left_frame.columnconfigure(0, weight=1)
        left_frame.columnconfigure(1, weight=1)
        left_frame.columnconfigure(2, weight=1)
        left_frame.columnconfigure(3, weight=1)

        # Right Frame
        ttk.Label(right_frame, text="Inventory Summary", font=self.font.get_font("regular4"), foreground="black",
                  bootstyle="inverse-light", anchor=ttk.W).grid(row=0, column=1, sticky="nwes")

        ne_frame = ttk.Frame(right_frame, relief="ridge", bootstyle="", padding=2)
        ne_frame.grid(row=1, column=1, columnspan=3, sticky="nwes", pady=5)

        ttk.Label(right_frame, text="QUANTITY IN STOCK", font=self.font.get_font("thin5"), anchor=ttk.W,
                  foreground=self.styleObj.colors.get('dark')).grid(row=1, column=1, sticky="w", padx=4)
        ttk.Label(right_frame, text=self.db_connection.query_stock_quantity(), font=self.font.get_font("regular4"),
                  anchor=ttk.E).grid(row=1, column=3, sticky="we", padx=10)
        ttk.Separator(ne_frame, orient="vertical").grid(row=0, column=1, sticky="nse")

        ne_frame.rowconfigure(0, weight=1)
        ne_frame.columnconfigure(0, weight=4)
        ne_frame.columnconfigure(1, weight=1)
        ne_frame.columnconfigure(2, weight=1)

        se_frame = ttk.Frame(right_frame, relief="ridge", bootstyle="", padding=2)
        se_frame.grid(row=2, column=1, columnspan=3, sticky="nwes", pady=5)

        ttk.Label(right_frame, text="QUANTITY TO BE RECEIVED", font=self.font.get_font("thin5"), anchor=ttk.W,
                  foreground=self.styleObj.colors.get('dark')).grid(row=2, column=1, sticky="w", padx=4)
        ttk.Label(right_frame, text=self.db_connection.query_shipment_quantity(), font=self.font.get_font("regular4"),
                  anchor=ttk.E).grid(row=2, column=3, sticky="we", padx=10)
        ttk.Separator(se_frame, orient="vertical").grid(row=0, column=1, sticky="nse")

        se_frame.rowconfigure(0, weight=1)
        se_frame.columnconfigure(0, weight=4)
        se_frame.columnconfigure(1, weight=1)
        se_frame.columnconfigure(2, weight=1)

        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=0)
        right_frame.rowconfigure(2, weight=0)
        right_frame.columnconfigure(1, weight=1)

    def configure_bottom_frame(self, bottom_frame: ttk.Frame):
        # Create Frames
        northwest_frame = ttk.Frame(bottom_frame, relief="ridge", padding=10)
        northwest_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        southwest_frame = ttk.Frame(bottom_frame, relief="ridge", padding=10)
        southwest_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        northeast_frame = ttk.Frame(bottom_frame, relief="ridge", padding=10)
        northeast_frame.grid(row=0, column=2, columnspan=2, sticky="nsew", padx=10, pady=10)

        southeast_frame = ttk.Frame(bottom_frame, padding=10, bootstyle="light")
        southeast_frame.grid(row=1, column=1, columnspan=3, sticky="nsew", padx=10, pady=10)

        bottom_frame.rowconfigure(0, weight=1)
        bottom_frame.rowconfigure(1, weight=1)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(2, weight=1)
        bottom_frame.columnconfigure(3, weight=1)

        # Northwest Frame
        self._product_details_frame(northwest_frame)

        # Southwest Frame
        ttk.Label(southwest_frame, text="Task Details", font=self.font.get_font("header4"), foreground="black",
                  anchor=ttk.W).grid(row=0, column=1, columnspan=2, sticky="nwes")
        ttk.Separator(southwest_frame).grid(row=1, column=1, columnspan=2, sticky="nwe")
        ttk.Label(southwest_frame, text="Remaining Tasks", font=self.font.get_font("header5"), anchor=ttk.S,
                  foreground=self.styleObj.colors.get('secondary')).grid(row=2, column=1, sticky="swe")
        ttk.Label(southwest_frame, text=len(self.db_connection.query_task_updatable()),
                  font=self.font.get_font("header6"), anchor=ttk.N, foreground=self.styleObj.colors.get("danger")
                  ).grid(row=3, column=1, sticky="nwe")

        southwest_frame.rowconfigure(0, weight=0)
        southwest_frame.rowconfigure(1, weight=0)
        southwest_frame.rowconfigure(2, weight=1)
        southwest_frame.rowconfigure(3, weight=1)
        southwest_frame.columnconfigure(1, weight=1)

        # Northeast Frame
        ttk.Label(northeast_frame, text="Top Selling Items", font=self.font.get_font("header4"), foreground="black",
                  anchor=ttk.W).grid(row=0, column=1, columnspan=5, sticky="nwes")
        ttk.Separator(northeast_frame).grid(row=1, column=1, columnspan=5, sticky="nwe")
        ttk.Label(northeast_frame, text="No. 1", font=self.font.get_font("header2"), anchor=ttk.CENTER,
                  foreground="black").grid(row=2, column=1, sticky="nwes")
        ttk.Separator(northeast_frame, orient="vertical").grid(row=2, column=2, rowspan=4, sticky="ns")
        ttk.Label(northeast_frame, text="No. 2", font=self.font.get_font("header2"), anchor=ttk.CENTER,
                  foreground=self.styleObj.colors.get('dark')).grid(row=2, column=3, sticky="nwes")
        ttk.Separator(northeast_frame, orient="vertical").grid(row=2, column=4, rowspan=4, sticky="ns")
        ttk.Label(northeast_frame, text="No. 3", font=self.font.get_font("header2"), anchor=ttk.CENTER,
                  foreground=self.styleObj.colors.get('secondary')).grid(row=2, column=5, sticky="nwes")

        for index, detail in enumerate(self.db_connection.query_product_popular(), start=1):
            ttk.Label(northeast_frame, text=detail[0], font=self.font.get_font("thin2"),
                      foreground=self.styleObj.colors.get("dark")).grid(row=3, column=2*index-1)
            ttk.Label(northeast_frame, text=detail[1], font=self.font.get_font("thin2"),
                      foreground=self.styleObj.colors.get("dark")).grid(row=4, column=2*index-1)
            frame = ttk.Frame(northeast_frame)
            frame.grid(row=5, column=2*index-1, sticky="nsew")
            ttk.Label(frame, text=detail[2], anchor=ttk.E, font=self.font.get_font("header4")
                      ).grid(row=1, column=1, sticky="ew")
            ttk.Label(frame, text="pcs", anchor=ttk.W, font=self.font.get_font("thin6"),
                      foreground=self.styleObj.colors.get("primary")).grid(row=1, column=2, sticky="ew")
            frame.rowconfigure(1, weight=1)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=1)

        northeast_frame.rowconfigure(0, weight=0)
        northeast_frame.rowconfigure(1, weight=0)
        northeast_frame.rowconfigure(2, weight=1)
        northeast_frame.rowconfigure(3, weight=0)
        northeast_frame.rowconfigure(4, weight=0)
        northeast_frame.rowconfigure(5, weight=1)
        northeast_frame.columnconfigure(1, weight=1)
        northeast_frame.columnconfigure(2, weight=0)
        northeast_frame.columnconfigure(3, weight=1)
        northeast_frame.columnconfigure(4, weight=0)
        northeast_frame.columnconfigure(5, weight=1)

        # Southeast Frame
        ttk.Label(southeast_frame, text="Purchase Activity", font=self.font.get_font("regular4"), foreground="black",
                  anchor=ttk.W, bootstyle="inverse-light").grid(row=0, column=1, columnspan=4, sticky="nwes", pady=0)

        parameters = self.db_connection.query_purchaseOrder_dashboard()
        self._info_frame(southeast_frame, 1, parameters[0], "primary", "Purchase Order Created")
        self._info_frame(southeast_frame, 2, parameters[1], "danger", "Purchase Order In Transit")
        self._info_frame(southeast_frame, 3, parameters[2], "success", "Purchase Order Received")
        self._info_frame(southeast_frame, 4, parameters[3], "primary", "Stock Purchased")

        southeast_frame.rowconfigure(0, weight=1)
        southeast_frame.rowconfigure(1, weight=1)
        southeast_frame.columnconfigure(1, weight=1)
        southeast_frame.columnconfigure(2, weight=1)
        southeast_frame.columnconfigure(3, weight=1)
        southeast_frame.columnconfigure(4, weight=1)

    def _product_details_frame(self, west_frame):
        parameters = self.db_connection.query_product_dashboard()
        ttk.Label(west_frame, text="Product Details", font=self.font.get_font("header4"), foreground="black",
                  anchor=ttk.W).grid(row=0, column=1, columnspan=2, sticky="nwes")
        ttk.Separator(west_frame).grid(row=1, column=1, columnspan=2, sticky="nwe")
        left_frame = ttk.Frame(west_frame)
        left_frame.grid(row=2, column=1, sticky="nwes")
        ttk.Label(left_frame, text="Low Stock Items", font=self.font.get_font("thin2"), anchor=ttk.W,
                  foreground=self.styleObj.colors.get("danger")).grid(row=0, column=0, sticky="w")
        ttk.Label(left_frame, text="Product Categories", font=self.font.get_font("thin2"), anchor=ttk.W,
                  foreground="black").grid(row=1, column=0, sticky="w")
        ttk.Label(left_frame, text="Product Types", font=self.font.get_font("thin2"), anchor=ttk.W,
                  foreground="black").grid(row=2, column=0, sticky="w")
        ttk.Label(left_frame, text="Products Out Of Stock", font=self.font.get_font("thin2"), anchor=ttk.W,
                  foreground=self.styleObj.colors.get("danger")).grid(row=3, column=0, sticky="w")
        ttk.Label(left_frame, text=parameters[0], font=self.font.get_font("thin2"), anchor=ttk.E,
                  foreground=self.styleObj.colors.get('danger')).grid(row=0, column=0, sticky="e")
        ttk.Label(left_frame, text=parameters[1], font=self.font.get_font("thin2"), anchor=ttk.E,
                  foreground="black").grid(row=1, column=0, sticky="e")
        ttk.Label(left_frame, text=parameters[2], font=self.font.get_font("thin2"), anchor=ttk.E,
                  foreground="black").grid(row=2, column=0, sticky="e")
        ttk.Label(left_frame, text=parameters[3], font=self.font.get_font("thin2"), anchor=ttk.E,
                  foreground=self.styleObj.colors.get('danger')).grid(row=3, column=0, sticky="e")
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(2, weight=1)
        left_frame.rowconfigure(3, weight=1)
        left_frame.columnconfigure(0, weight=1)
        right_frame = ttk.Frame(west_frame)
        right_frame.grid(row=2, column=2)
        ttk.Label(right_frame, text="Active Products", font=self.font.get_font("thin3"), anchor=ttk.CENTER,
                  foreground=self.styleObj.colors.get("dark")).grid(row=0, column=0, sticky="we")
        parameters = self.db_connection.query_product_meter()
        print(parameters)
        ttk.Meter(right_frame, amounttotal=parameters[0] if parameters[0] else 1, amountused=parameters[1],
                  bootstyle="success",
                  meterthickness=15, stripethickness=int(360 / int(parameters[0])) if parameters[0] else 1,
                  metersize=200,
                  textfont=self.font.get_font("header5"), subtext="Products In Stock", textright=f"/{parameters[0]}",
                  subtextfont=self.font.get_font("thin6")).grid(row=1, column=0, sticky="nwes")
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        west_frame.rowconfigure(0, weight=0)
        west_frame.rowconfigure(1, weight=0)
        west_frame.rowconfigure(2, weight=1)
        west_frame.columnconfigure(1, weight=1)
        west_frame.columnconfigure(2, weight=1)

    def _info_frame(self, parent: ttk.Frame, column: int,  qty: int, qty_style: ttk.Style.theme_names, info: str):
        frame = ttk.Frame(parent, bootstyle="", padding=10, relief="raised", borderwidth=5)
        frame.grid(row=1, column=column, sticky="nwes", padx=5)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text=str(qty), bootstyle=f"{qty_style}", anchor=ttk.N, font=self.font.get_font(
            "regular5")).grid(row=0, column=0, sticky="nwe")
        ttk.Label(frame, text="QTY", foreground=self.styleObj.colors.get("secondary"), anchor=ttk.S,
                  font=self.font.get_font("thin4")).grid(row=0, column=0, sticky="swe")
        ttk.Frame(frame, height=10).grid(row=2, column=0, sticky="nwes")
        ttk.Label(frame, text=info, font=self.font.get_font("thin3"), foreground=self.styleObj.colors.get(
            "dark"), anchor=ttk.CENTER).grid(row=3, column=0, sticky="nwe")




if __name__ == "__main__":
    from navigationFrame import navigationFrame

    # Create Main Window, and center it
    window = ttk.Window(title="Keai IWMS", themename="litera", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    # Creates Frames
    lFrame = navigationFrame(window, 1, ttk.Frame(window))
    lFrame.getButtonCommand("Dashboard")

    # Starts Event Main Loop
    window.mainloop()
