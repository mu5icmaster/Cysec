import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from PIL import ImageTk, Image

from utils import fonts, previewText, validation
from Database.Database import DatabaseConnection
from Database.Authentication import authentication
from configuration import Configuration
from Frames.popup import popup


class AccountsPopup(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(title="Accounts", takefocus=True)  #, transient=parent)
        self.place_window_center()

        self.fonts = fonts()
        self.styleObj = ttk.style.Style.get_instance()
        self.db_connection = DatabaseConnection()
        self.config = Configuration()
        graphicsPath = self.config.getGraphicsPath()

        self.images = [Image.open(f'{graphicsPath}/passwordInvisible.png').resize((24, 24)),
                       Image.open(f'{graphicsPath}/passwordVisible.png').resize((32, 32))]
        self.image_objects = [ImageTk.PhotoImage(image=im) for im in self.images]

        # Create Frames
        title_frame = ttk.Frame(self, bootstyle="warning")
        button_frame = ttk.Frame(self, padding=10)
        tableview_frame = ttk.Frame(self)

        title_frame.grid(row=0, column=0, sticky="nsew")
        button_frame.grid(row=1, column=0, sticky="nsew")
        tableview_frame.grid(row=2, column=0, sticky="nsew")

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Title Frame
        ttk.Label(title_frame, text="Accounts", font=self.fonts.get_font("header2"), bootstyle="inverse-warning",
                  foreground="black", padding=10).grid(row=0, column=0, sticky="nw")
        ttk.Separator(title_frame, orient="horizontal").grid(row=1, column=0, sticky="sew")
        title_frame.rowconfigure(0, weight=1)
        title_frame.columnconfigure(0, weight=1)

        # Button Frame
        self.styleObj.configure(style="warning.TButton", font=self.fonts.get_font("regular2"), foreground="black")
        for index, text in enumerate(["Add", "Edit", "Delete"]):
            ttk.Button(button_frame, text=text, bootstyle="warning", command=lambda x=text: (
                self.get_button_command(x))).grid(row=1, column=index + 1, sticky="nsew", padx=5)

        button_frame.rowconfigure(1, weight=1)
        button_frame.columnconfigure(0, weight=5)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        # Tableview
        self.tableview = Tableview(
            master=tableview_frame,
            searchable=True,
            stripecolor=(self.styleObj.colors.get("light"), None),
            autofit=True,
            bootstyle="danger"
        )
        self.tableview.grid(row=0, column=0, sticky="nsew")

        y_scrollbar = ttk.Scrollbar(tableview_frame, orient="vertical",
                                    command=self.tableview.winfo_children()[1].yview,
                                    bootstyle="secondary-round")
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        colNames = ["No.", "Name", "Role", "Email", "Contact Number"]
        for colName in colNames:
            self.tableview.insert_column(index="end", text=colName, anchor="center", stretch=True)
        self.update_tableview()

        tableview_frame.rowconfigure(0, weight=1)
        tableview_frame.columnconfigure(0, weight=1)

    def get_button_command(self, button_text: str):
        if button_text == "Add":
            self.add_popup()

        elif button_text == "Edit":
            self.edit_popup()

        elif button_text == "Delete":
            self.delete_popup()

    def update_tableview(self):
        self.tableview.delete_rows()
        for value in self.db_connection.query_accounts_table():
            self.tableview.insert_row("end", value)
        self.tableview.load_table_data()

    def add_popup(self):
        def onSubmitButton():
            auth = authentication()
            if not auth.createAccount(employeeName=toplevel.stringVar[0].get(),
                                      employeeRoleID=toplevel.stringVar[1].get().split(' - ')[0],
                                      employeeEmail=toplevel.stringVar[2].get(),
                                      employeeContactNumber=toplevel.stringVar[3].get(),
                                      employeePassword=toplevel.stringVar[4].get()
                                      ):
                toplevel.errVar[-1].set("Submission failed to process")
            else:
                self.update_tableview()
                toplevel.destroy()

        # Create Popup
        toplevel = popup(master=self, title="Add Employee", entryFieldQty=5)
        toplevel.create_title_frame(toplevel.frameList[0], title="Add Employee")
        toplevel.focus()

        # Create Widgets
        for i, e in enumerate(["Employee Name", "Employee Role", "Employee Email", "Employee Contact Number",
                               "Employee Password"], start=1):
            toplevel.create_label(toplevel.frameList[i], e)
            toplevel.create_errMsg(toplevel.frameList[i], toplevel.errVar[i - 1])
        toplevel.create_entry(toplevel.frameList[1], toplevel.stringVar[0])
        toplevel.create_combobox(toplevel.frameList[2], toplevel.stringVar[1], options=["1 - Administrator",
                                                                                        "2 - Supervisor", "3 - Worker"])
        toplevel.create_entry(toplevel.frameList[3], toplevel.stringVar[2])
        toplevel.create_entry(toplevel.frameList[4], toplevel.stringVar[3])
        toplevel.create_entry(toplevel.frameList[5], toplevel.stringVar[4])
        toplevel.create_buttonbox(toplevel.frameList[6])
        toplevel.submitButton.configure(command=lambda: onSubmitButton())

        # Password entry shenanigans
        canvas = ttk.Canvas(toplevel.frameList[5], width=42, height=42)
        canvas.grid(row=1, column=1, sticky="wes")
        toplevel.entries[4] = ttk.Entry(canvas, textvariable=toplevel.stringVar[4])

        self.styleObj.configure(style="light.TButton", background="white", borderwidth=0)
        button = ttk.Button(canvas, bootstyle="light", padding=-1.5)
        self._hide_password(toplevel.entries[4], button)

        canvas.create_window(0, 0, anchor="nw", window=toplevel.entries[4], tags="entry")
        canvas.create_window(0, 0, anchor="center", window=button, tags="button")

        canvas.bind("<Configure>", lambda event: canvas.itemconfig("entry", width=canvas.winfo_width()))
        canvas.bind("<Configure>", lambda event: canvas.coords("button", canvas.winfo_width() - 15, 15), add="+")

        # Preview Text
        for i, e in enumerate(["employeeNameEntry", "employeeRoleEntry", "emailEntry", "contactNumberEntry",
                               "passwordEntry"]):
            previewText(toplevel.entries[i], key=e)
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Validation
        valObj = validation()
        valObj.validate(widget=toplevel.entries[0], key="string", errStringVar=toplevel.errVar[0])
        valObj.validate(widget=toplevel.entries[1], key="role", errStringVar=toplevel.errVar[1])
        valObj.validate(widget=toplevel.entries[2], key="email", errStringVar=toplevel.errVar[2])
        valObj.validate(widget=toplevel.entries[3], key="contactNumber", errStringVar=toplevel.errVar[3])
        valObj.validate(widget=toplevel.entries[4], key="password", errStringVar=toplevel.errVar[4])

        # Configure grids
        for i in range(1, 6):
            toplevel.configure_frame(toplevel.frameList[i])
        toplevel.configure_toplevel()

    def edit_popup(self):

        def onSubmitButton():
            auth = authentication()
            if not auth.updateAccount(employeeName=toplevel.stringVar[0].get().split(' - ')[1],
                                    employeeRoleID=toplevel.stringVar[1].get().split(' - ')[0],
                                    employeeEmail=toplevel.stringVar[2].get(),
                                    employeeContactNumber=toplevel.stringVar[3].get(),
                                    employeePassword=toplevel.stringVar[4].get(),
                                    employeeID=toplevel.stringVar[0].get().split(' - ')[0]
                                    ):
                toplevel.errVar[-1].set("Submission failed to process")
            else:
                self.update_tableview()
                toplevel.destroy()

        def onNameEntry():
            if toplevel.stringVar[0].get() in toplevel.entries[0].cget("value"):
                toplevel.entries[1].configure(value=["1 - Administrator", "2 - Supervisor", "3 - Worker"])
                for i in range(1, 5):
                    toplevel.entries[i].configure(state="enabled")

            else:
                for i in range(1, 5):
                    toplevel.entries[i].configure(state="readonly", foreground=self.styleObj.colors.get("secondary"))
                toplevel.entries[1].configure(value=[])
                toplevel.stringVar[1].set("Employee Role")
                toplevel.stringVar[2].set("abc@companyKEAI.com")
                toplevel.stringVar[3].set("60161234567")
                toplevel.stringVar[4].set("abcd1234!")

        # Create Popup
        toplevel = popup(master=self, title="Edit Employee", entryFieldQty=5)
        toplevel.create_title_frame(toplevel.frameList[0], title="Edit Employee")
        toplevel.focus()

        # Create Widgets
        for i, e in enumerate(["Employee Name", "Employee Role", "Employee Email", "Employee Contact Number",
                               "Employee Password"], start=1):
            toplevel.create_label(toplevel.frameList[i], e)
            toplevel.create_errMsg(toplevel.frameList[i], toplevel.errVar[i - 1])
        toplevel.create_combobox(toplevel.frameList[1], toplevel.stringVar[0], options=[
            f"{i[0]} - {i[1]}" for i in self.db_connection.query_accounts_table()])
        toplevel.create_combobox(toplevel.frameList[2], toplevel.stringVar[1], state="readonly")
        toplevel.create_entry(toplevel.frameList[3], toplevel.stringVar[2], state="readonly")
        toplevel.create_entry(toplevel.frameList[4], toplevel.stringVar[3], state="readonly")
        toplevel.create_entry(toplevel.frameList[5], toplevel.stringVar[4], state="readonly")
        toplevel.create_buttonbox(toplevel.frameList[6])
        toplevel.submitButton.configure(command=lambda: onSubmitButton())

        # Password entry shenanigans
        canvas = ttk.Canvas(toplevel.frameList[5], width=42, height=42)
        canvas.grid(row=1, column=1, sticky="wes")
        toplevel.entries[4] = ttk.Entry(canvas, textvariable=toplevel.stringVar[4], state="readonly")

        self.styleObj.configure(style="light.TButton", background="white", borderwidth=0)
        button = ttk.Button(canvas, bootstyle="light", padding=-1.5)
        self._hide_password(toplevel.entries[4], button)

        canvas.create_window(0, 0, anchor="nw", window=toplevel.entries[4], tags="entry")
        canvas.create_window(0, 0, anchor="center", window=button, tags="button")

        canvas.bind("<Configure>", lambda event: canvas.itemconfig("entry", width=canvas.winfo_width()))
        canvas.bind("<Configure>", lambda event: canvas.coords("button", canvas.winfo_width() - 15, 15), add="+")

        # Preview Text
        for i, e in enumerate(["employeeNameEntry", "employeeRoleEntry", "emailEntry", "contactNumberEntry",
                               "passwordEntry"]):
            previewText(toplevel.entries[i], key=e)

        toplevel.stringVar[0].trace("w", lambda x, y, z: onNameEntry())

        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Validation
        valObj = validation()
        valObj.validate(widget=toplevel.entries[1], key="role", errStringVar=toplevel.errVar[1])
        valObj.validate(widget=toplevel.entries[2], key="email", errStringVar=toplevel.errVar[2])
        valObj.validate(widget=toplevel.entries[3], key="contactNumber", errStringVar=toplevel.errVar[3])
        valObj.validate(widget=toplevel.entries[4], key="password", errStringVar=toplevel.errVar[4])

        # Insert row details
        try:
            rowDetails = self.tableview.get_row(iid=self.tableview.view.focus()).values
            toplevel.stringVar[0].set(f"{rowDetails[0]} - {rowDetails[1]}")
            toplevel.stringVar[1].set([value for value in ["1 - Administrator", "2 - Supervisor", "3 - Worker"] if
                                       value.split(' - ')[1] == rowDetails[2]][0])
            toplevel.stringVar[2].set(rowDetails[3])
            toplevel.stringVar[3].set(rowDetails[4])
            for i in range(0, 4):
                toplevel.entries[i].configure(foreground="black")
        except:
            rowDetails = []

        # Configure grids
        for i in range(1, 6):
            toplevel.configure_frame(toplevel.frameList[i])
        toplevel.configure_toplevel()

    def delete_popup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        if popup.deleteDialog(self) == "OK":
            if self.db_connection.deleteAccount(rowDetails[0]):
                self.update_tableview()
            else:
                popup.deleteFail(self)


    def _show_password(self, entry: ttk.Entry, button: ttk.Button):
        entry.configure(show="")
        button.configure(image=self.image_objects[1], command=lambda: self._hide_password(entry, button))

    def _hide_password(self, entry: ttk.Entry, button: ttk.Button):
        entry.configure(show="*")
        button.configure(image=self.image_objects[0], command=lambda: self._show_password(entry, button))


if __name__ == "__main__":
    window = ttk.Window(title="Test Page", themename="flatly")
    window.withdraw()

    AccountsPopup(window).edit_popup()

    window.mainloop()
