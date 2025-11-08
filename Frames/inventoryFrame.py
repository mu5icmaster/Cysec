from Frames.pageFrame import *
from Database.Database import DatabaseConnection
from ttkbootstrap.validation import validator, add_validation
import re

from Frames.popup import popup


class inventoryFrame(pageFrame):

    def __init__(self, master: ttk.Window, role: str, employeeID: int) -> None:

        # Inherits Page Frame
        super().__init__(master=master,
                         title="Inventory",
                         role=role,
                         button_config={
                             "Worker": ["Receive", "Update", "Delete"],
                             "Supervisor": ["Receive", "Update", "Delete"],
                             "Administrator": ["Receive", "Update", "Delete"]
                         },
                         employeeID=employeeID)

        # Inserts Tableview columns
        colNames = ["Inventory ID", "Product No","Name", "Description", "Quantity", "Location", "Batch Number ID"]
        self._insert_table_headings(colNames)

        self.db_connection = DatabaseConnection()
        self._load_table_rows(self.db_connection.query_inventory_table())

    def _insert_table_headings(self, colNames:list) -> None:
        for name in colNames:
            self._insert_table_columns(name)

    def getButtonCommand(self, button_text):
        if button_text == "Receive":
            self.receivePopup()

        elif button_text == "Update":
            self.updatePopup()

        elif button_text == "Delete":
            self.deletePopup()

    def receivePopup(self):

        receivables = self.db_connection.query_purchaseOrder_receivables()
        shipmentIDs = [value[0] for value in receivables]
        #print(receivables)
        def onProductNoEntry():
            try:
                values = [value for value in receivables if value[0] == toplevel.stringVar[0].get()][0]
                for index, value in enumerate(values):
                    toplevel.stringVar[index].set(value)
                    toplevel.entries[index].configure(foreground="black")

            except:
                for index, value in enumerate(["FUR-Type-Size-Color-Number", "Archaic Chair", "The chair, a silent sentinel, bore witness to the passage of time.", "Vendor Name", "0"]):
                    toplevel.stringVar[index+1].set(value)
                    toplevel.entries[index+1].configure(foreground=self.styleObj.colors.get("secondary"))

        def onSubmitButton():
            if not self.db_connection.receive_inventory(toplevel.stringVar[0].get()):
                toplevel.errVar[5].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_inventory_table())
                toplevel.destroy()


        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Receive Inventory", entryFieldQty=6)

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Receive Inventory")
        for index, key in enumerate(["Shipment No", "Product No", "Product Name", "Product Description", "Quantity","Vendor"]):
            toplevel.create_label(frame=toplevel.frameList[index+1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index+1], errVar=toplevel.errVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], options=shipmentIDs)
        for index in range(1,6):
            toplevel.create_entry(frame=toplevel.frameList[index+1], stringVar=toplevel.stringVar[index], state="readonly")
        toplevel.create_buttonbox(frame=toplevel.frameList[7])
        toplevel.submitButton.configure(command= lambda: onSubmitButton())

        # Preview Text
        for index, value in enumerate(["shipmentNoEntry", "productNoEntry", "productNameEntry", "productDescriptionEntry", "0Entry", "vendorNameEntry"]):
            previewText(toplevel.entries[index], key=value)

        toplevel.stringVar[0].trace("w", lambda x, y, z: onProductNoEntry())

        # Validation
        valObj = validation()
        valObj.validate(toplevel.entries[0], key="shipmentNo", errStringVar=toplevel.errVar[0])

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range (1, 7):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def updatePopup(self):

        try:
            rowDetails = self.tableview.get_row(iid=self.tableview.view.focus()).values
            if rowDetails[-2] == "Output":
                popup.infoPopup(self, "Row selected is already located at Output.")
                return
        except:
            rowDetails = []
        updatables = self.db_connection.query_inventory_updatable()

        def onSubmitButton():
            parameters = [toplevel.stringVar[0].get().split(' - ')[0], toplevel.stringVar[3].get().split(' (')[0],
                          toplevel.stringVar[2].get().split(' - ')[0], toplevel.stringVar[5].get().split(' - ')[0], toplevel.stringVar[4].get()]
            #print(parameters)
            if not self.db_connection.update_inventory(*parameters):
                toplevel.errVar[6].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_inventory_table())
                toplevel.destroy()

        def onProductEntry(*args, **kwargs):
            #print(f"Function called\n{toplevel.stringVar[0].get()}\n{updatables}")
            if toplevel.stringVar[0].get() in updatables.keys():
                toplevel.stringVar[1].set(updatables[toplevel.stringVar[0].get()])
                toplevel.entries[1].configure(foreground="black")
                toplevel.entries[2].configure(state="enabled")
            else:
                toplevel.stringVar[1].set("The chair, a silent sentinel, bore witness to the passage of time.")
                toplevel.stringVar[2].set("Choose a location")
                toplevel.entries[2].configure(state="readonly")
                for i in [1,2]:
                    toplevel.entries[i].configure(foreground=self.styleObj.colors.get("secondary"))

        def onSrcLocationEntry(*args, **kwargs):
            options = []
            for value in toplevel.entries[2].cget("values"):
                options += [value]
            if toplevel.stringVar[2].get() in options:
                toplevel.entries[3].configure(state="enabled")
                toplevel.entries[5].configure(state="enabled")
            else:
                for index, value in enumerate(["BATCH-YYMMDD-[A-Z]", "0", "Choose a location"]):
                    toplevel.stringVar[index+3].set(value)
                    toplevel.entries[index+3].configure(foreground=self.styleObj.colors.get("secondary"), state="readonly")
                toplevel.entries[4].configure(to=0)

        def onBatchEntry(*args, **kwargs):
            if toplevel.stringVar[3].get() in toplevel.entries[3].cget("values"):
                toplevel.entries[4].configure(foreground= "black", state="enabled", to= re.search(r"[(]\d+", string=toplevel.stringVar[3].get()).group()[1:])
            else:
                toplevel.stringVar[4].set("0")
                toplevel.entries[4].configure(foreground=self.styleObj.colors.get("secondary"), state="readonly", to=0)

        def desLocationEntryValidation(event):
            #print(f"Value:{toplevel.stringVar[4].get()}\nValues:{toplevel.entries}")
            if toplevel.stringVar[5].get().split(' (')[0] not in toplevel.entries[5].cget("values"):
                toplevel.errVar[5].set("Invalid Warehouse Location")
                return False
            toplevel.errVar[5].set("")
            return True

        def quantityEntryValidation(event):
            if float(toplevel.stringVar[4].get()) < 0 or float(toplevel.stringVar[4].get())>float(toplevel.entries[4].cget("to")):
                toplevel.errVar[4].set("Invalid Quantity Selected")
                return False
            try:
                int(toplevel.stringVar[4].get())
            except:
                toplevel.errVar[4].set("Only integers allowed")
                return False
            toplevel.errVar[4].set("")
            return True

        def srcLocationPostCommand():
            if toplevel.stringVar[0].get() in updatables.keys():
                toplevel.entries[2].configure(values=self.db_connection.query_inventory_location(toplevel.stringVar[0].get().split(' - ')[0]))
            else:
                toplevel.entries[2].configure(values=[])
            #print(f"Product No: {toplevel.stringVar[0].get().split(' - ')[0]}\nOptions: {self.db_connection.query_inventory_location(toplevel.stringVar[0].get().split(' - ')[0])}")

        def batchPostCommand():
            if toplevel.stringVar[2].get() in toplevel.entries[2].cget("values"):
                toplevel.entries[3].configure(values=self.db_connection.query_inventory_productBatch(toplevel.stringVar[0].get().split(' - ')[0], toplevel.stringVar[2].get().split(' - ')[0]))
            else:
                toplevel.entries[3].configure(values=[])

        def desLocationPostCommand():
            options = ["1 - Input", "2 - Warehouse", "3 - Packing Zone", "4 - Output"]
            if toplevel.stringVar[2].get() in toplevel.entries[2].cget("values"):
                for index, value in enumerate(options):
                    #print(f"{toplevel.stringVar[2].get()}, {toplevel.stringVar[2].get().split(' (')}")
                    if value == toplevel.stringVar[2].get().split(' (')[0]:
                        options = options[index + 1:]
                        break
            else:
                options=[]
            toplevel.entries[5].configure(values=options)


        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Update Inventory", entryFieldQty=6)

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Update Inventory")
        for index, key in enumerate(["Product No.", "Product Description", "Source Location", "Product Batch No.", "Quantity", "Destination Location"]):
            toplevel.create_label(frame=toplevel.frameList[index + 1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index + 1], errVar=toplevel.errVar[index])

        toplevel.create_combobox(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], options=[key for key in updatables.keys()])
        toplevel.create_entry(frame=toplevel.frameList[2], stringVar=toplevel.stringVar[1], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[3], stringVar=toplevel.stringVar[2], state="readonly", postcommand=lambda: srcLocationPostCommand())
        toplevel.create_combobox(frame=toplevel.frameList[4], stringVar=toplevel.stringVar[3], state="readonly", postcommand=lambda: batchPostCommand())
        toplevel.create_spinbox(frame=toplevel.frameList[5], stringVar=toplevel.stringVar[4], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[6], stringVar=toplevel.stringVar[5], state="readonly", postcommand=lambda: desLocationPostCommand())
        toplevel.create_buttonbox(frame=toplevel.frameList[7])
        toplevel.submitButton.configure(command = lambda: onSubmitButton())
        toplevel.entries[4].configure(to=0)

        # Preview Text
        previewText(toplevel.entries[0], key="inventoryProductEntry")
        previewText(toplevel.entries[1], key="productDescriptionEntry")
        previewText(toplevel.entries[2], key="locationEntry")
        previewText(toplevel.entries[3], key="productBatchEntry")
        previewText(toplevel.entries[4], key="0Entry")
        previewText(toplevel.entries[5], key="locationEntry")

        toplevel.stringVar[0].trace("w", onProductEntry)
        toplevel.stringVar[2].trace("w", onSrcLocationEntry)
        toplevel.stringVar[3].trace("w", onBatchEntry)

        if rowDetails != []:
            #print(rowDetails)
            toplevel.stringVar[0].set(f"{rowDetails[1]} - {rowDetails[2]}")
            srcLocationPostCommand()
            for option in toplevel.entries[2].cget("values"):
                if rowDetails[5] == option.split(' - ')[1].split(' (')[0]:
                    toplevel.stringVar[2].set(option)
            batchPostCommand()
            for option in toplevel.entries[3].cget("values"):
                if rowDetails[6] == option.split(' (')[0]:
                    toplevel.stringVar[3].set(option)
            for i in [0,2,3]:
                toplevel.entries[i].configure(foreground="black")

        # Validation
        add_validation(toplevel.entries[4], validator(quantityEntryValidation), when="focus")
        add_validation(toplevel.entries[5], validator(desLocationEntryValidation), when="focus")

        # Bindings
        toplevel.bind_entry_return()
        toplevel.traceButton()

        # Configure Frames
        for index in range(1, 7):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def deletePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        if popup.deleteDialog(self) == "OK":
            #print(rowDetails)
            if self.db_connection.delete_inventory(rowDetails[0]):
                self._load_table_rows(self.db_connection.query_inventory_table())
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
    rFrame = inventoryFrame(window, "Worker", employeeID=3)
    lFrame = navigationFrame(window, 3, rFrame)
    #rFrame.createPopup()

    # Starts Event Main Loop
    window.mainloop()