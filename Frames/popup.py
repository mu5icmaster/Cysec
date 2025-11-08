from abc import ABC

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification

from utils import fonts, validation


class popup(ttk.window.Toplevel, ABC):

    def __init__(self, master: ttk.window.Window, title: str, entryFieldQty: int, **kwargs) -> None:

        # Inherit TopLevel widget
        super().__init__(title=title, transient=master, topmost=True, **kwargs)
        self.place_window_center()
        self.grab_set()

        # Font Object Reference
        self.font = fonts()

        # Initialise variables
        self.frameList = [ttk.Frame(self, padding=10) for _ in range(entryFieldQty+2)]
        self.frameList[0].configure(padding=0, bootstyle="warning")
        self.stringVar = [ttk.StringVar() for _ in range(entryFieldQty)]
        self.errVar = [ttk.StringVar() for _ in range(entryFieldQty + 1)]
        self.entries = []
        self.errLabels = []

        # Use public methods to place widgets in self.frameList
        # Call preview objects on self.entries
        # Bind validations to self.entries, then change self.errLabels

    def create_title_frame(self, frame: ttk.Frame, title: str) -> None:
        label = ttk.Label(frame, text=title, bootstyle="warning-inverse", foreground="black", anchor="center", font=self.font.get_font("header2"))
        label.grid(row=1, column=1, sticky="nwes")

        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

    def create_label(self, frame: ttk.Frame, label: str) -> None:
        label = ttk.Label(frame, text=label)
        label.grid(row=0, column=1, sticky="sw")

    def create_entry(self, frame: ttk.Frame, stringVar: ttk.StringVar, state = "enabled") -> None:
        if state == "enabled":
            entry = ttk.Entry(master=frame, textvariable=stringVar, state="enabled")
        elif state == "readonly":
            entry = ttk.Entry(master=frame, textvariable=stringVar, state="readonly")
        else:
            print(f"Entry field created with invalid state \nFrame: {frame}\nState: {state}")
        #print(entry.cget("state"))
        entry.grid(row=1, column=1, sticky="we")
        self.entries += [entry]

    def create_dateEntry(self, frame: ttk.Frame, stringVar: ttk.StringVar, state = "enabled") -> None:
        if state == "enabled":
            entry = ttk.DateEntry(master=frame, dateformat=r"%Y-%m-%d",firstweekday=0)
            entry.entry.configure(textvariable=stringVar, state="enabled")
        elif state == "readonly":
            entry = ttk.DateEntry(master=frame, dateformat=r"%Y-%m-%d",firstweekday=0)
            entry.entry.configure(textvariable=stringVar, state="readonly")
        else:
            print(f"Entry field created with invalid state \nFrame: {frame}\nState: {state}")
        #print(entry.cget("state"))
        entry.grid(row=1, column=1, sticky="we")
        self.entries += [entry.entry]

    def create_spinbox(self, frame: ttk.Frame, stringVar: ttk.StringVar, state = "enabled", to=1000) -> None:
        if state == "enabled":
            entry = ttk.Spinbox(master=frame, textvariable=stringVar, state="enabled", increment=1, from_=0, to=to)
        elif state == "readonly":
            entry = ttk.Spinbox(master=frame, textvariable=stringVar, state="readonly", increment=1, from_=0, to=to)
        else:
            print(f"Spinbox field created with invalid state \nFrame: {frame}\nState: {state}")
        #print(entry.cget("state"))
        entry.grid(row=1, column=1, sticky="we")
        self.entries += [entry]

    def create_combobox(self, frame: ttk.Frame, stringVar: ttk.StringVar, options: list = [], state= "enabled", postcommand=None):
        if state == "enabled":
            #print(postcommand)
            entry = ttk.Combobox(master=frame, textvariable=stringVar, values=options, postcommand=postcommand)
        elif state == "readonly":
            entry = ttk.Combobox(master=frame, textvariable=stringVar, values=options, state="readonly", postcommand=postcommand)
        else:
            print(f"Combobox created with invalid state \nFrame: {frame}\nState: {state}")

        entry.grid(row=1, column=1, sticky="we")
        self.entries += [entry]

    def create_errMsg(self, frame: ttk.Frame, errVar: ttk.StringVar) -> None:
        errMsg = ttk.Label(master=frame, textvariable=errVar, foreground=ttk.style.Style.get_instance().theme.colors.get("danger"), font=self.font.get_font("error"))
        errMsg.grid(row=2, column=1, sticky="nwe")
        self.errLabels += [errMsg]

    def create_buttonbox(self, frame: ttk.Frame):
        #print(f"Function given: {command}")
        self.submitButton = ttk.Button(master=frame, text="Submit", bootstyle="success", state="disabled")
        self.submitButton.focus_set()
        self.submitButton.grid(row=1, column=2, sticky="e")

        cnl_btn = ttk.Button(master=frame, text="Cancel", command=lambda: self.destroy(), bootstyle="danger")
        cnl_btn.grid(row=1, column=1, sticky="e")

        errVar = ttk.StringVar()
        self.errVar += [errVar]
        errMsg = ttk.Label(master=frame, textvariable=errVar, foreground=ttk.style.Style.get_instance().theme.colors.get("danger"), font=self.font.get_font("error"))
        errMsg.grid(row=2, column=0, columnspan=3, sticky="ne")

        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=0)
        frame.columnconfigure(0, weight=20)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

    @staticmethod
    def deleteDialog(parent:ttk.TTK_WIDGETS) -> str:
        """Returns: 'OK' or 'Cancel' """
        return Messagebox.okcancel(message="Action cannot be undone. Proceed to deletion?", title="Warning", parent=parent)

    @staticmethod
    def deleteFail(parent:ttk.TTK_WIDGETS) -> Messagebox.show_info:
        return Messagebox.show_info(title="Info", message="Operation failed. There are likely linked data entries in the existing database.", parent=parent)

    @staticmethod
    def infoPopup(parent:ttk.TTK_WIDGETS, msg:str) -> Messagebox.show_info:
        return Messagebox.show_info(title="Info", message=msg, parent=parent)

    @staticmethod
    def getTableRows(tableview:ttk.tableview) -> list:
        try:
            rowDetails = tableview.get_row(iid=tableview.view.focus()).values
            return rowDetails
        except:
            ToastNotification(
                title="Please select a table row",
                message="Please select the details you would you like to operate on.",
                duration=3000
            ).show_toast()
            return []

    # Enables submit button if all entry fields are not greyed out
    def validateButton(self):
        if validation.validateButton(self.submitButton, self.stringVar, self.entries):
            self.submitButton.configure(state="enabled")
        else:
            self.submitButton.configure(state="disabled")

    # Binds all entries to validateButon
    def traceButton(self):
        for entry in self.entries:
            #print(f"Entry Traced: {entry}")
            entry.bind("<FocusOut>", lambda event: self.validateButton(), add="+")
            entry.bind("<KeyRelease>", lambda event: self.validateButton(), add="+")
            entry.bind("<ButtonRelease>", lambda event: self.validateButton(), add="+")

    # Binds enter to the next entry field
    def bind_entry_return(self):
        next_index = 1
        for index in range(1, len(self.entries)):
            self.entries[index - 1].bind("<Return>",lambda event, x=next_index: self.entries[x].focus())
            next_index += 1
        self.entries[-1].bind("<Return>", lambda event: self.submitButton.focus())

    def configure_frame(self, frame):
        """Configure Entry Field frames only"""
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(1, weight=1)

    def configure_toplevel(self):
        for index, frame in enumerate(self.frameList, start=1):
            frame.grid(row=index, column=1, sticky="nwes")
            self.rowconfigure(index, weight=1)
        self.rowconfigure(len(self.frameList)+1, weight=1)
        self.columnconfigure(1, weight=1)
