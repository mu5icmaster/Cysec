import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from PIL import ImageTk, Image
from utils import fonts
from configuration import Configuration
from Database import Notification
from datetime import datetime


class notificationFrame(ttk.Frame):

    def __init__(self, master: ttk.Window, employee_id: int) -> None:
        self.master = master
        self.employee_id = employee_id
        self.Fonts = fonts()
        self.styleObj = ttk.style.Style.get_instance()
        self.config = Configuration()
        self.notif = Notification(employee_id)
        graphicsPath = self.config.getGraphicsPath()
        self.icon = Image.open(f'{graphicsPath}/notificationIcon.png').resize((40, 40))
        self.icon = ImageTk.PhotoImage(image=self.icon)
        self.xButton = Image.open(f'{graphicsPath}/xButton.png').resize((8, 8))
        self.xButton = ImageTk.PhotoImage(image=self.xButton)

        # Creates and places Notification Frame
        super().__init__(master, bootstyle="secondary")
        self.placeNotificationFrame()
        master.bind("<Configure>", lambda event: self.placeNotificationFrame(), add="+")

        # Create Widgets
        topFrame = ttk.Frame(self, bootstyle="warning")
        bottomFrame = ScrolledFrame(self, bootstyle="secondary-round")
        bottomFrame.configure(style="TFrame", padding=10)
        lSeparator = ttk.Separator(self, bootstyle="dark", orient="vertical")

        notification = ttk.Label(topFrame, bootstyle="inverse-warning", text="Notifications", anchor="center", font=self.Fonts.get_font("regular"), foreground="black")
        notificationButton = ttk.Button(topFrame, image=self.icon, bootstyle="warning", command=lambda: self.destroy())
        bSeparator = ttk.Separator(topFrame, bootstyle="dark")

        # Grid Frames
        topFrame.grid(row=0, column=1, sticky="nwes")
        bottomFrame.grid(row=1, column=1, sticky="nwes")
        lSeparator.grid(row=0, column=0, rowspan=2, sticky="nws")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Top Frame Widgets
        notification.grid(row=0, column=0, sticky="nwes")
        notificationButton.grid(row=0, column=1, sticky="nwes")
        bSeparator.grid(row=1, column=0, columnspan=2, sticky="wes")

        topFrame.rowconfigure(0, weight=1)
        topFrame.rowconfigure(1, weight=0)
        topFrame.columnconfigure(0, weight=1)
        topFrame.columnconfigure(1, weight=1)

        # Bottom Frame Widgets
        self.configure_bottomFrame(bottomFrame)

    def configure_bottomFrame(self, bottomFrame):
        for child in bottomFrame.winfo_children():
            child.destroy()
        bottomFrame.grid_forget()

        notifications = self.notif.get_notifications()
        for i, notification in enumerate(
                sorted(notifications, key=lambda x: datetime.strptime(x[1], "%Y-%m-%d %H:%M:%S.%f"))):
            # Create a frame for each notification
            frame = ttk.Frame(bottomFrame, bootstyle="light", relief="ridge", padding=2)
            frame.grid(row=i, column=1, sticky="nwes", pady=2)

            # Convert Timestamp
            timestamp = datetime.strptime(notification[1], "%Y-%m-%d %H:%M:%S.%f")
            if (timestamp - datetime.today()).days >= 1:
                timestamp = timestamp.strftime("%A, %dth %B")
            else:
                timestamp = timestamp.strftime("%H:%M:%S")

            # Configure Labels
            ttk.Label(frame, text=f"Notification {notification[0]}", font=self.Fonts.get_font("thin4"), anchor=ttk.NW,
                      bootstyle="inverse-light", foreground=self.styleObj.colors.get("dark")).grid(
                row=0, column=1, sticky="nwes")
            self.styleObj.configure("grey.secondary.TButton", background=self.styleObj.colors.get("light"),
                                    borderwidth=0)
            ttk.Button(frame, image=self.xButton, style="grey.secondary.TButton",
                       command=lambda x=bottomFrame, y=notification[0]: self._xButton(x, y)).grid(
                       row=0, column=2, sticky="ne")
            ttk.Label(frame, text=notification[2], font=self.Fonts.get_font("thin2"), anchor=ttk.CENTER,
                      bootstyle="inverse-light", foreground="black", wraplength=240).grid(
                      row=1, column=1, columnspan=2, sticky="nwes")
            ttk.Label(frame, text=timestamp, font=self.Fonts.get_font("thin4"), anchor=ttk.NE,
                      bootstyle="inverse-light", foreground=self.styleObj.colors.get("dark")).grid(
                      row=2, column=2, sticky="nwes")

            frame.rowconfigure(1, weight=1)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=1)

            bottomFrame.rowconfigure(i, weight=1)
        ttk.Frame(bottomFrame, width=8).grid(row=0, column=2)
        bottomFrame.columnconfigure(0, weight=0)
        bottomFrame.columnconfigure(1, weight=1)

        bottomFrame.grid(row=1, column=1, sticky="nwes")

    def _xButton(self, bottomFrame, notification_id):
        self.config.writeNotificationExclusions(self.employee_id, notification_id)
        self.configure_bottomFrame(bottomFrame)

    def placeNotificationFrame(self):
        #print("Place called")
        width = 0.2*self.master.winfo_width()
        height = self.master.winfo_height()
        #print("W"+ str(width) + " H" + str(height))
        try:
            self.place(relx=0.8, rely=0, width=width, height=height)
        except:
            pass


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
    lFrame.getButtonCommand("Inventory")
    notifs = notificationFrame(window, 1)
    window.mainloop()
