from Frames.pageFrame import *
from Database import DatabaseConnection, Notification

from Frames.popup import popup


class productFrame(pageFrame):

    def __init__(self, master: ttk.Window, role: str, employeeID: int) -> None:

        # Inherits Page Frame
        super().__init__(master=master,
                         title="Product",
                         role=role,
                         button_config={
                             "Supervisor": ["Create", "Update", "Delete"],
                             "Administrator": ["Create", "Update", "Delete"]
                         },
                         employeeID=employeeID)

        # Inserts Tableview columns
        colNames = ["Product No", "Name", "Description", "Price", "Quantity", "Preferred Vendor"]
        self._insert_table_headings(colNames)

        self.db_connection = DatabaseConnection()
        self._load_table_rows(self.db_connection.query_product_table())

    def _insert_table_headings(self, colNames:list) -> None:
        for name in colNames:
            self._insert_table_columns(name)

    def getButtonCommand(self, button_text):
        if button_text == "Create":
            self.createPopup()

        elif button_text == "Update":
            self.updatePopup()

        elif button_text == "Delete":
            self.deletePopup()

    def createPopup(self):
        # Database Query
        vendors = [f"{vendorID} - {vendorName}" for vendorID, vendorName in self.db_connection.query_vendor()]

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Create Product", entryFieldQty=5)

        def onSubmitButton():
            parameters = [i.get() for i in toplevel.stringVar]
            parameters[-1] = parameters[-1].split(' - ')[0]
            # print(parameters)
            if not self.db_connection.add_product(*parameters):
                toplevel.errVar[-1].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_product_table())
                toplevel.destroy()


        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Create Product")
        for index, key in enumerate(["Product No.", "Name", "Description", "Price (RM)", "Preferred Vendor"]):
            toplevel.create_label(frame=toplevel.frameList[index + 1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index + 1], errVar=toplevel.errVar[index])
        for index in range(4):
            toplevel.create_entry(frame=toplevel.frameList[index + 1], stringVar=toplevel.stringVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[5], stringVar=toplevel.stringVar[4], options=vendors)
        toplevel.create_buttonbox(frame=toplevel.frameList[6])
        toplevel.submitButton.configure(command= lambda: onSubmitButton())

        # Preview Text
        previewText(toplevel.entries[0], key="productNoEntry")
        previewText(toplevel.entries[1], key="productNameEntry")
        previewText(toplevel.entries[2], key="productDescriptionEntry")
        previewText(toplevel.entries[3], key="priceEntry")
        previewText(toplevel.entries[4], key="preferredVendorEntry")

        # Validation
        valObj = validation()
        for index, key in enumerate(["productNo", "string", "string", "price", "vendor"]):
            valObj.validate(widget=toplevel.entries[index], key=key, errStringVar=toplevel.errVar[index])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range(1, 6):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def updatePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        #print(rowDetails)

        # Database Query
        vendors = [f"{vendorID} - {vendorName}" for vendorID, vendorName in self.db_connection.query_vendor()]
        rowDetails += [f"{ID[0]} - {rowDetails[-1]}" for ID in self.db_connection.query_vendor() if ID[1] == rowDetails[-1]]
        rowDetails.pop(-2)
        rowDetails.pop(-2)

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Update Product", entryFieldQty=5)

        def onSubmitButton():
            parameters = [i.get() for i in toplevel.stringVar]
            parameters[-1] = int(parameters[-1].split(' - ')[0])
            parameters[-2] = float(parameters[-2])
            print(*parameters)
            if not self.db_connection.update_product(*parameters):
                toplevel.errVar[-1].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_product_table())
                toplevel.destroy()

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Update Product")
        for index, key in enumerate(["Product No.", "Name", "Description", "Price (RM)", "Preferred Vendor"]):
            toplevel.create_label(frame=toplevel.frameList[index + 1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index + 1], errVar=toplevel.errVar[index])
        for index in range(4):
            toplevel.create_entry(frame=toplevel.frameList[index + 1], stringVar=toplevel.stringVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[5], stringVar=toplevel.stringVar[4], options=vendors)
        toplevel.create_buttonbox(frame=toplevel.frameList[6])
        toplevel.submitButton.configure(command= lambda: onSubmitButton())
        toplevel.entries[0].configure(state="readonly")

        # Preview Text
        previewText(toplevel.entries[0], key="productNoEntry")
        previewText(toplevel.entries[1], key="productNameEntry")
        previewText(toplevel.entries[2], key="productDescriptionEntry")
        previewText(toplevel.entries[3], key="priceEntry")
        previewText(toplevel.entries[4], key="preferredVendorEntry")

        for index, value in enumerate(rowDetails):
            toplevel.stringVar[index].set(value)
            toplevel.entries[index].configure(foreground="black")

        # Validation
        valObj = validation()
        for index, key in enumerate(["string", "string", "price", "vendor"], start=1):
            valObj.validate(widget=toplevel.entries[index], key=key, errStringVar=toplevel.errVar[index])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range(1, 6):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def deletePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        if popup.deleteDialog(self) == "OK":
            if self.db_connection.delete_product(rowDetails[0]):
                self._load_table_rows(self.db_connection.query_product_table())
            else:
                popup.deleteFail(self)

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
    lFrame.getButtonCommand("Product")
    #rFrame.createPopup()

    # Starts Event Main Loop
    window.mainloop()