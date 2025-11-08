from abc import ABC, abstractmethod
from utils import *
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from PIL import Image, ImageTk

from Frames.notificationFrame import notificationFrame
from configuration import Configuration


class pageFrame(ttk.Frame, ABC):

    def __init__(self, master: ttk.Window, title: str, button_config: dict, role: str, employeeID: int) -> None:
        """
        Abstract base class of a page frame.

        Args:
            master (ttk.Window): Master window.
            title (str): Page header.
            button_config (dict): Key->["Worker", "Supervisor", "Administrator];
                                  Values should be a list of all valid buttons.
            role (str): Role of operator.
        """

        # Inherit ttk.Frame
        super().__init__(master)
        self.grid(row=0, column=1, sticky="nwes")

        # Create references
        self.masterWindow = master
        self.button_config = button_config
        self.employeeID = employeeID
        self.role = role
        self.styleObj = ttk.style.Style.get_instance()
        self.font = fonts()
        self.config = Configuration()
        graphicsPath = self.config.getGraphicsPath()
        self.images = [
            Image.open(f'{graphicsPath}/notificationIcon.png').resize((50, 50))
        ]
        self.imageObject = []
        for im in self.images:
            self.imageObject += [ImageTk.PhotoImage(image=im)]

        # Create Frames
        topFrame = ttk.Frame(self)
        topFrame.grid(row=1, column=1, sticky="nwes")

        bottomFrame = ttk.Frame(self)
        bottomFrame.grid(row=2, column=1, sticky="nwes")

        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=20)
        self.columnconfigure(1, weight=1)

        # Top Frame Widgets
        productLabel = ttk.Label(topFrame, text=title, font=self.font.fonts["header3"])
        self.styleObj.configure(style="light.TButton", background="white", borderwidth=0)
        notificationButton = ttk.Button(topFrame, image=self.imageObject[0], bootstyle="light",
                                        command=lambda: notificationFrame(self.masterWindow, self.employeeID))
        productLabel.grid(row=1, column=1, sticky="nw", padx=20, pady=20)
        notificationButton.grid(row=1, column=2, sticky="nes")

        buttonFrame = ttk.Frame(topFrame, padding=20)
        buttonFrame.grid(row=2, column=1, columnspan=2, sticky="nwes")
        self._create_buttons(buttonFrame)

        topFrame.rowconfigure(1, weight=1)
        topFrame.rowconfigure(2, weight=3)
        topFrame.columnconfigure(1, weight=1)
        topFrame.columnconfigure(2, weight=0)

        # Bottom Frame Widgets
        self.tableview = Tableview(
            master=bottomFrame,
            searchable=True,
            stripecolor=(self.styleObj.theme.colors.get("light"), None),
            autofit=True,
            bootstyle="primary"
        )
        self.tableview.grid(row=1, column=1, sticky="nwes")

        y_scrollbar = ttk.Scrollbar(bottomFrame, orient="vertical", command=self.tableview.winfo_children()[1].yview,
                                    bootstyle="secondary-round")
        y_scrollbar.grid(row=1, column=2, sticky="ns")

        bottomFrame.rowconfigure(1, weight=1)
        bottomFrame.columnconfigure(1, weight=1)

    def _create_buttons(self, buttonFrame: ttk.Frame) -> None:
        self.styleObj.configure(style="warning.TButton", font=self.font.get_font("regular2"), foreground="black")
        for col, button_text in enumerate(self.button_config.get(self.role, []), start=1):
            button = ttk.Button(buttonFrame, text=button_text, bootstyle="warning",
                                command=lambda x=button_text: self.getButtonCommand(x))
            button.grid(row=1, column=col, sticky="nwes", padx=5)

        buttonFrame.rowconfigure(1, weight=1)
        if self.role == "Worker":
            buttonFrame.columnconfigure(0, weight=5)
        buttonFrame.columnconfigure(tuple(range(1, len(self.button_config.get(self.role, [])) + 1)), weight=1)

    @abstractmethod
    def _insert_table_headings(self, colNames: list) -> None:
        """For col in List: self._insert_table_columns(col)"""
        pass

    def _insert_table_columns(self, colName: str) -> None:
        self.tableview.insert_column(
            index="end",
            text=colName,
            anchor="center",
            stretch=True
        )

    def _load_table_rows(self, rowList: list) -> None:
        self.tableview.delete_rows()
        for list in rowList:
            self.tableview.insert_row('end', list)
        self.tableview.load_table_data()

    @abstractmethod
    def getButtonCommand(self, button_text):
        pass
