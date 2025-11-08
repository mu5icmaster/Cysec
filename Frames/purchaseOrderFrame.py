from Frames.pageFrame import *
from Frames.popup import popup


class purchaseOrderFrame(pageFrame):

    def __init__(self, master: ttk.Window, role: str, employeeID: int) -> None:

        # Inherits Page Frame
        super().__init__(master=master,
                         title="Purchase Order",
                         role=role,
                         button_config={
                             "Supervisor": ["Create", "Update", "Delete"],
                             "Administrator": ["Create", "Update", "Delete"]
                         },
                         employeeID=employeeID)

        # Inserts Tableview columns
        colNames = ["Purchase No", "Product Name", "Quantity Bought", "Batch Number ID", "Vendor Name", "Date", "Status"]
        self._insert_table_headings(colNames)

        self.db_connection = DatabaseConnection()
        self._load_table_rows(self.db_connection.query_purchaseOrder())

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

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Create Purchase Order", entryFieldQty=5, load_table_callback=self._load_table_rows(self.db_connection.query_purchaseOrder()))

        def onProductEntry(*args, **kwargs):
            #print(f"Value: {toplevel.stringVar[0].get()}\nOptions: {[f'{ID} - {NAME}' for ID, NAME, DESC in self.db_connection.query_product()]}")
            if toplevel.stringVar[0].get() in [f"{ID} - {NAME}" for ID, NAME, DESC in self.db_connection.query_product()]:
                #print(self.db_connection.query_productDescription(toplevel.stringVar[0].get().split(' - ')[0]))
                toplevel.stringVar[1].set(self.db_connection.query_productDescription(toplevel.stringVar[0].get().split(' - ')[0]))
                toplevel.entries[1].configure(foreground="black")
                toplevel.entries[2].configure(state="enabled")
                toplevel.stringVar[4].set(self.db_connection.query_preferred_vendor(toplevel.stringVar[0].get().split(' - ')[0]))
                toplevel.entries[4].configure(foreground="black")
            else:
                toplevel.stringVar[1].set("The chair, a silent sentinel, bore witness to the passage of time.")
                toplevel.stringVar[2].set("0")
                toplevel.stringVar[4].set("Vendor Name")
                for i in [1,2]:
                    toplevel.entries[i].configure(foreground=self.styleObj.colors.get("secondary"), state="readonly")
                toplevel.entries[4].configure(foreground=self.styleObj.colors.get("secondary"))
        def onQuantityEntry(*args, **kwargs):
            if toplevel.entries[2].cget("state") != "enabled":
                #print("Invalid Entry")
                toplevel.stringVar[2].set("0")
            else:
                toplevel.entries[2].configure(foreground="black")

        def onButtonPress():
            parameters =[]
            for i in [0, 2, 4, 3]:
                parameters += [toplevel.stringVar[i].get()]
            for i in [0, 2]:
                parameters[i] = parameters[i].split(' - ')[0]
            #print(*parameters)
            if not self.db_connection.add_purchaseOrder(*parameters):
                toplevel.errVar[-1].set("Submission failed to process.")
            else:
                self._load_table_rows(self.db_connection.query_purchaseOrder())
                toplevel.destroy()

        def productPostCommand():
            options = [f"{ID} - {NAME}" for ID, NAME, DESC in self.db_connection.query_product()]
            toplevel.entries[0].configure(value=options)

        def vendorPostComannd():
            options = []
            for i in self.db_connection.query_vendor():
                options += [f"{i[0]} - {i[1]}"]
            toplevel.entries[4].configure(value=options)


        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Create Purchase Order")
        for index, key in enumerate(["Product ID", "Product Description", "Quantity", "Batch Number ID", "Vendor Name"]):
            toplevel.create_label(frame=toplevel.frameList[index+1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index+1], errVar=toplevel.errVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], postcommand=productPostCommand)
        toplevel.create_entry(frame=toplevel.frameList[2], stringVar=toplevel.stringVar[1], state="readonly")
        toplevel.create_spinbox(frame=toplevel.frameList[3], stringVar=toplevel.stringVar[2], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[4], stringVar=toplevel.stringVar[3], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[5], stringVar=toplevel.stringVar[4], postcommand=vendorPostComannd)
        toplevel.create_buttonbox(frame=toplevel.frameList[6])
        toplevel.submitButton.configure(command=onButtonPress)

        #print(toplevel.entries)

        options = self.db_connection.query_productBatch_today()
        toplevel.stringVar[3].set(options[-1])
        toplevel.entries[3].configure(value=options)

        # Preview Text
        entryList =["productIDEntry", "productDescriptionEntry", "0Entry"]
        for index, value in enumerate(entryList):
            previewText(toplevel.entries[index], key=value)
        previewText(toplevel.entries[4], key="vendorNameEntry")

        toplevel.stringVar[0].trace("w", onProductEntry)
        toplevel.stringVar[2].trace("w", onQuantityEntry)


        # Validation
        valObj = validation()
        valObj.validate(widget=toplevel.entries[4], key="vendor", errStringVar=toplevel.errVar[4])
        valObj.validate(widget=toplevel.entries[2], key="integer", errStringVar=toplevel.errVar[2])
        #for index in [0, 1]:
        #    valObj.validate(widget=toplevel.entries[index], key="integer", errStringVar=toplevel.errVar[index])
        #valObj.validate(widget=toplevel.entries[2], key="string", errStringVar=toplevel.errVar[2])
        #valObj.validate(widget=toplevel.entries[3], key="string", errStringVar=toplevel.errVar[3])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range (1, 6):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def updatePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        print(rowDetails)

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Create Purchase Order", entryFieldQty=7,
                         load_table_callback=self._load_table_rows(self.db_connection.query_purchaseOrder()))

        def onProductEntry(*args, **kwargs):
            # print(f"Value: {toplevel.stringVar[0].get()}\nOptions: {[f'{ID} - {NAME}' for ID, NAME, DESC in self.db_connection.query_product()]}")
            if toplevel.stringVar[1].get() in [f"{ID} - {NAME}" for ID, NAME, DESC in
                                               self.db_connection.query_product()]:
                # print(self.db_connection.query_productDescription(toplevel.stringVar[0].get().split(' - ')[0]))
                toplevel.stringVar[2].set(
                    self.db_connection.query_productDescription(toplevel.stringVar[1].get().split(' - ')[0]))
                toplevel.entries[2].configure(foreground="black")
                toplevel.entries[3].configure(state="enabled")
                toplevel.stringVar[5].set(
                    self.db_connection.query_preferred_vendor(toplevel.stringVar[1].get().split(' - ')[0]))
                toplevel.entries[5].configure(foreground="black")
            else:
                toplevel.stringVar[2].set("The chair, a silent sentinel, bore witness to the passage of time.")
                toplevel.stringVar[3].set("0")
                toplevel.stringVar[5].set("Vendor Name")
                for i in [2, 3]:
                    toplevel.entries[i].configure(foreground=self.styleObj.colors.get("secondary"), state="readonly")
                toplevel.entries[5].configure(foreground=self.styleObj.colors.get("secondary"))

        def onQuantityEntry(*args, **kwargs):
            if toplevel.entries[3].cget("state") != "enabled":
                # print("Invalid Entry")
                toplevel.stringVar[3].set("0")
            else:
                toplevel.entries[3].configure(foreground="black")

        def onButtonPress():
            parameters = []
            for i in [0, 1, 3, 5, 6]:
                parameters += [toplevel.stringVar[i].get()]
            for i in [1, 3]:
                #print(parameters[i])
                #print(parameters[i].split(' - '))
                parameters[i] = parameters[i].split(' - ')[0]
            #print(*parameters)
            if not self.db_connection.update_purchaseOrder(*parameters):
                toplevel.errVar[-1].set("Submission failed to process.")
            else:
                self._load_table_rows(self.db_connection.query_purchaseOrder())
                toplevel.destroy()

        def productPostCommand():
            options = [f"{ID} - {NAME}" for ID, NAME, DESC in self.db_connection.query_product()]
            toplevel.entries[1].configure(value=options)

        def vendorPostComannd():
            options = []
            for i in self.db_connection.query_vendor():
                options += [f"{i[0]} - {i[1]}"]
            toplevel.entries[5].configure(value=options)

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Update Purchase Order")
        for index, key in enumerate(
                ["Shipment ID","Product ID", "Product Description", "Quantity", "Batch Number ID", "Vendor Name", "Status"]):
            toplevel.create_label(frame=toplevel.frameList[index + 1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index + 1], errVar=toplevel.errVar[index])
        toplevel.create_entry(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[2], stringVar=toplevel.stringVar[1],
                                 postcommand=productPostCommand)
        toplevel.create_entry(frame=toplevel.frameList[3], stringVar=toplevel.stringVar[2], state="readonly")
        toplevel.create_spinbox(frame=toplevel.frameList[4], stringVar=toplevel.stringVar[3], state="readonly")
        toplevel.create_entry(frame=toplevel.frameList[5], stringVar=toplevel.stringVar[4], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[6], stringVar=toplevel.stringVar[5],
                                 postcommand=vendorPostComannd)
        toplevel.create_combobox(frame=toplevel.frameList[7], stringVar=toplevel.stringVar[6], state="readonly")
        toplevel.create_buttonbox(frame=toplevel.frameList[8])
        toplevel.submitButton.configure(command=onButtonPress)

        # Preview Text
        entryList = ["productIDEntry", "productDescriptionEntry", "0Entry"]
        for index, value in enumerate(entryList):
            previewText(toplevel.entries[index+1], key=value)
        previewText(toplevel.entries[5], key="vendorNameEntry")

        toplevel.stringVar[1].trace("w", onProductEntry)
        toplevel.stringVar[3].trace("w", onQuantityEntry)

        #print(self.db_connection.query_productID(rowDetails[1]))
        toplevel.stringVar[1].set(self.db_connection.query_productID(rowDetails[1]))
        toplevel.entries[1].configure(foreground="black")
        toplevel.entries[3].set(rowDetails[2])
        toplevel.stringVar[4].set(rowDetails[3])
        toplevel.stringVar[6].set(rowDetails[-1])
        toplevel.entries[6].configure(value=["Not Received", "In Transit"])
        toplevel.stringVar[0].set(rowDetails[0])

        # Validation
        valObj = validation()
        valObj.validate(widget=toplevel.entries[5], key="vendor", errStringVar=toplevel.errVar[4])
        valObj.validate(widget=toplevel.entries[3], key="integer", errStringVar=toplevel.errVar[2])
        # for index in [0, 1]:
        #    valObj.validate(widget=toplevel.entries[index], key="integer", errStringVar=toplevel.errVar[index])
        # valObj.validate(widget=toplevel.entries[2], key="string", errStringVar=toplevel.errVar[2])
        # valObj.validate(widget=toplevel.entries[3], key="string", errStringVar=toplevel.errVar[3])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range(1, 8):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def deletePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        if popup.deleteDialog(self) == "OK":
            if self.db_connection.delete_purchaseOrder(rowDetails[0]):
                self._load_table_rows(self.db_connection.query_purchaseOrder())
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
    rFrame = purchaseOrderFrame(window, "Administrator", 1)
    lFrame = navigationFrame(window, 1, rFrame)
    #rFrame.createPopup()

    # Starts Event Main Loop
    window.mainloop()