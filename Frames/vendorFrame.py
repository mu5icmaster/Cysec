from Frames.pageFrame import *
from Database.Database import DatabaseConnection

from Frames.popup import popup


class vendorFrame(pageFrame):

    def __init__(self, master: ttk.Window, role: str, employeeID: int) -> None:

        # Inherits Page Frame
        super().__init__(master=master,
                         title="Vendors",
                         role=role,
                         button_config={
                             "Supervisor": ["Add", "Update", "Delete"],
                             "Administrator": ["Add", "Update", "Delete"]
                         }, employeeID=employeeID)

        # Inserts Tableview columns
        colNames = ["Vendor ID", "Vendor Name", "Email", "Contact Number"]
        self._insert_table_headings(colNames)

        self.db_connection = DatabaseConnection()
        self._load_table_rows(self.db_connection.query_vendor_all())

    def _insert_table_headings(self, colNames:list) -> None:
        for name in colNames:
            self._insert_table_columns(name)

    def getButtonCommand(self, button_text):
        if button_text == "Add":
            self.addPopup()

        elif button_text == "Update":
            self.updatePopup()

        elif button_text == "Delete":
            self.deletePopup()

    def addPopup(self):

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Add Vendor", entryFieldQty=4)

        def onButtonPress():
            if not self.db_connection.add_vendor(toplevel.stringVar[1].get(), toplevel.stringVar[2].get(), toplevel.stringVar[3].get()):
                toplevel.errVar[3].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_vendor_all())
                toplevel.destroy()

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Add Vendor")
        for index, key in enumerate(["Vendor ID", "Vendor Name", "Email", "Contact Number"]):
            toplevel.create_label(frame=toplevel.frameList[index+1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index+1], errVar=toplevel.errVar[index])
            toplevel.create_entry(frame=toplevel.frameList[index+1], stringVar= toplevel.stringVar[index])
        toplevel.create_buttonbox(frame=toplevel.frameList[5])
        toplevel.submitButton.configure(command= lambda: onButtonPress())

        try:
            vendorID = self.db_connection.query_vendor()[-1][0] + 1
        except IndexError:
            vendorID = 1
        #print(vendorID)
        toplevel.entries[0].configure(state="readonly")
        toplevel.stringVar[0].set(str(vendorID))

        # Preview Text
        entryList =["vendorNameEntry", "emailEntry", "contactNumberEntry"]
        for index, value in enumerate(entryList):
            previewText(toplevel.entries[index+1], key=value)

        # Validation
        valObj = validation()
        valObj.validate(widget=toplevel.entries[0], key="integer", errStringVar=toplevel.errVar[0])
        valObj.validate(widget=toplevel.entries[1], key="string", errStringVar=toplevel.errVar[1])
        valObj.validate(widget=toplevel.entries[2], key="email", errStringVar=toplevel.errVar[2])
        valObj.validate(widget=toplevel.entries[3], key="contactNumber", errStringVar=toplevel.errVar[3])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range (1, 5):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def updatePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        def onButtonPress():
            parameters = []
            for i in [0,1,3,2]:
                parameters+= [toplevel.stringVar[i].get()]
            if not self.db_connection.update_vendor(*parameters):
                toplevel.errVar[4].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_vendor_all())
                toplevel.destroy()

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Update Vendor", entryFieldQty=4)

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Update Vendor")
        for index, key in enumerate(["Vendor ID", "Vendor Name", "Email", "Contact Number"]):
            toplevel.create_label(frame=toplevel.frameList[index+1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index+1], errVar=toplevel.errVar[index])
            toplevel.create_entry(frame=toplevel.frameList[index+1], stringVar= toplevel.stringVar[index])
        toplevel.create_buttonbox(frame=toplevel.frameList[5])
        toplevel.submitButton.configure(command= lambda : onButtonPress())

        # Preview Text
        entryList =["vendorNameEntry", "emailEntry", "contactNumberEntry"]
        for index, value in enumerate(entryList):
            previewText(toplevel.entries[index+1], key=value)

        toplevel.entries[0].configure(state="disabled")
        for index, value in enumerate(rowDetails):
            toplevel.entries[index].configure(foreground="black")
            toplevel.stringVar[index].set(value)

        # Validation
        valObj = validation()
        valObj.validate(widget=toplevel.entries[0], key="integer", errStringVar=toplevel.errVar[0])
        valObj.validate(widget=toplevel.entries[1], key="string", errStringVar=toplevel.errVar[1])
        valObj.validate(widget=toplevel.entries[2], key="email", errStringVar=toplevel.errVar[2])
        valObj.validate(widget=toplevel.entries[3], key="contactNumber", errStringVar=toplevel.errVar[3])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range (1, 5):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def deletePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        if popup.deleteDialog(self) == "OK":
            if self.db_connection.delete_vendor(rowDetails[0]):
                self._load_table_rows(self.db_connection.query_vendor_all())
            else:
                popup.deleteFail(self)

# Test Case
if __name__ == "__main__":
    from navigationFrame import navigationFrame

    # Create Main Window, and center it
    window = ttk.Window(title="Keai IWMS", themename="litera", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    # Creates Frames
    lFrame = navigationFrame(window, 1, ttk.Frame())
    lFrame.getButtonCommand("Vendor")
    #rFrame.createPopup()

    # Starts Event Main Loop
    window.mainloop()