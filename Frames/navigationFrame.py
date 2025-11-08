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


class navigationFrame(ttk.Frame):

    def __init__(self, master: ttk.window.Window, employeeID: int, rFrame: ttk.Frame) -> None:

        # Button Configuration for roles
        buttonConfig = {
            "Worker": ["Dashboard", "Inventory", "Report", "Tasks"],
            "Supervisor": ["Dashboard", "Product", "Inventory", "Purchase Order", "Sales Order", "Tasks", "Vendor",
                           "Report"],
            "Administrator": ["Dashboard", "Product", "Inventory", "Purchase Order", "Sales Order", "Vendor",
                              "Report", "Add Worker"]
        }

        # References
        self.Fonts = fonts()
        self.styleObj = master.style
        self.config = Configuration()
        self.master: ttk.window.Window = master
        self.rFrame = rFrame
        self.db_connection = Database.DatabaseConnection()
        self.employeeID = employeeID
        self.name = self.db_connection.query_employee(employeeID)[0]
        self.role = self.db_connection.query_employee(employeeID)[1]

        preferences = self.config.getPreferences(str(self.employeeID))
        self.styleObj.theme_use(preferences[1])

        # Inherit ttk.Frame, sets colour to warning
        super().__init__(master, bootstyle="warning")
        self.grid(row=0, column=0, sticky="nwes")

        # Application Images
        graphicsPath = self.config.getGraphicsPath()
        self.images = [
            Image.open(f'{graphicsPath}/settingsIcon.png').resize((40, 40)),
            self.make_circular_image(f'{graphicsPath}/User_Avatars/{preferences[0]}.png', 200)
        ]

        self.imageObject = []
        for im in self.images:
            self.imageObject += [ImageTk.PhotoImage(image=im)]

        # Create Widgets
        northFrame = ttk.Frame(self, bootstyle="warning", padding=20)
        southFrame = ttk.Frame(self, bootstyle="warning", padding=20)

        KEAILabel = ttk.Label(northFrame, text="KEAI", font=self.Fonts.fonts["header3"], bootstyle="warning-inverse",
                              foreground="black")
        settingsIcon = ttk.Button(northFrame, image=self.imageObject[0], bootstyle="warning",
                                  command=lambda: SettingsPopup(self.master, self.employeeID, self.redisplay_theme))
        profilePicture = ttk.Label(northFrame, image=self.imageObject[1],
                                   bootstyle="warning-inverse")
        userFrame = ttk.Frame(northFrame, bootstyle="warning")
        userName = ttk.Label(userFrame, text=self.name, font=self.Fonts.fonts["regular2"], bootstyle="warning-inverse",
                             foreground="black", anchor=ttk.CENTER)
        userID = ttk.Label(userFrame, text=str(self.role), font=self.Fonts.fonts["regular2"],
                           bootstyle="warning-inverse", foreground="black", anchor=ttk.CENTER)

        # Grid Frames
        northFrame.grid(row=0, column=0, sticky="nwes")
        southFrame.grid(row=1, column=0, sticky="nwes")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=1)

        # Grid North Frame
        KEAILabel.grid(row=1, column=1, sticky="nw")
        settingsIcon.grid(row=1, column=3, sticky="ne")
        profilePicture.grid(row=2, column=1, sticky="nws")
        userFrame.grid(row=2, column=2, columnspan=2, sticky="nwes")

        northFrame.rowconfigure(1, weight=1)
        northFrame.rowconfigure(2, weight=2)
        northFrame.columnconfigure(1, weight=1)
        northFrame.columnconfigure(2, weight=2)
        northFrame.columnconfigure(3, weight=1)

        # Grid User Frame
        userName.grid(row=1, column=1, sticky="swe")
        userID.grid(row=2, column=1, sticky="nwe")

        userFrame.rowconfigure(1, weight=1)
        userFrame.rowconfigure(2, weight=1)
        userFrame.columnconfigure(1, weight=1)

        # Create and grid buttons
        self.styleObj.configure(style="dark.Link.TButton", font=self.Fonts.get_font("regular2"), foreground="black")
        for row, button_text in enumerate(buttonConfig[self.role], start=1):
            button = ttk.Button(southFrame, text=button_text, bootstyle="dark-link",
                                command=lambda x=button_text: self.getButtonCommand(x))
            button.grid(row=row, column=1, sticky="we")
            southFrame.rowconfigure(row, weight=1)
        southFrame.rowconfigure(0, weight=1)
        southFrame.columnconfigure(1, weight=1)

        if self.role == "Worker":
            southFrame.rowconfigure(4, weight=10)
        else:
            southFrame.rowconfigure(8, weight=1)

    def getButtonCommand(self, button_text):
        if button_text == "Dashboard":
            self.rFrame.destroy()
            self.rFrame = DashboardFrame(self.master, self.role, self.employeeID)

        elif button_text == "Product":
            self.rFrame.destroy()
            self.rFrame = productFrame(self.master, self.role, self.employeeID)

        elif button_text == "Inventory":
            self.rFrame.destroy()
            self.rFrame = inventoryFrame(self.master, self.role, self.employeeID)

        elif button_text == "Purchase Order":
            self.rFrame.destroy()
            self.rFrame = purchaseOrderFrame(self.master, self.role, self.employeeID)

        elif button_text == "Sales Order":
            self.rFrame.destroy()
            self.rFrame = salesOrderFrame(self.master, self.role, self.employeeID)

        elif button_text == "Tasks":
            self.rFrame.destroy()
            self.rFrame = taskFrame(self.master, self.role, self.employeeID)

        elif button_text == "Vendor":
            self.rFrame.destroy()
            self.rFrame = vendorFrame(self.master, self.role, self.employeeID)

        elif button_text == "Report":
            self.rFrame.destroy()
            self.rFrame = ReportFrame(self.master, self.role, self.employeeID)

        elif button_text == "Add Worker":
            # Open the account creation dialog with Role dropdown enabled.
            # Admin can choose either Supervisor or Worker (default Worker).
            AccountSetupDialog(self.master, force_admin=False, fixed_role=None, on_success=lambda email: None)

    def redisplay_theme(self):
        jesus = {
            ".!dashboardframe": "Dashboard",
            ".!productframe": "Product",
            ".!inventoryframe": "Inventory",
            ".!purchaseorderframe": "Purchase Order",
            ".!salesorderframe": "Sales Order",
            ".!taskframe": "Tasks",
            ".!vendorframe": "Vendor"
        }
        for crucifix in jesus:
            if re.search(r".![a-z]+", str(self.rFrame)).group() == crucifix:
                frame = jesus[crucifix]
                break
        self.rFrame.destroy()
        self.destroy()
        new = navigationFrame(self.master, self.employeeID, self.rFrame)
        new.getButtonCommand(frame)

    def make_circular_image(self, image_path, output_diameter):

        img = Image.open(image_path).resize((output_diameter, output_diameter))

        mask = Image.new('L', (output_diameter, output_diameter), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, output_diameter, output_diameter), fill=255)

        output_img = Image.new(img.mode, (output_diameter, output_diameter), 0)
        output_img.paste(img, mask=mask)

        radius = int(output_diameter / 2)
        output_img = output_img.resize((radius, radius))

        return output_img


# Test Case
if __name__ == "__main__":
    # Create Main Window, and center it
    window = ttk.window.Window(title="Keai IWMS", themename="flatly", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    # Creates Navigation Frame
    rFrame = ttk.Frame(window)
    lFrame = navigationFrame(window, 1, rFrame)
    lFrame.getButtonCommand("Inventory")
    lFrame.redisplay_theme()

    # Starts Event Main Loop
    window.mainloop()
