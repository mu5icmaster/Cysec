import ttkbootstrap
import ttkbootstrap.scrolled
import ttkbootstrap.tableview
import ttkbootstrap.toast
from Frames.pageFrame import *
from Database.Database import DatabaseConnection
from ttkbootstrap.validation import add_validation, validator

from Frames.popup import popup


class salesOrderFrame(pageFrame):

    def __init__(self, master: ttk.Window, role: str, employeeID: int) -> None:

        # Inherits Page Frame
        super().__init__(master=master,
                         title="Sales Order",
                         role=role,
                         button_config={
                             "Supervisor": ["Add","Update",  "Delete", "Validate"],
                             "Administrator": ["Add", "Update", "Delete", "Validate"]
                         }, employeeID=employeeID)

        # Inserts Tableview columns
        colNames = ["Sale No.", "Product Sold", "Quantity", "Batch No.", "Date", "Status"]
        self._insert_table_headings(colNames)

        self.db_connection = DatabaseConnection()
        self._load_table_rows(self.db_connection.query_salesOrder_table())

    def _insert_table_headings(self, colNames:list) -> None:
        for name in colNames:
            self._insert_table_columns(name)

    def getButtonCommand(self, button_text):
        if button_text == "Add":
            self.addPopup()
            pass

        elif button_text == "Update":
            self.updatePopup()

        elif button_text == "Delete":
            self.deletePopup()

        elif button_text == "Validate":
            self.validatePopup()


    def addPopup(self):

        def onSubmitButton():
            if not self.db_connection.add_salesOrder(toplevel.stringVar[0].get(), toplevel.stringVar[1].get()[:1], toplevel.stringVar[3].get()):
                toplevel.errVar[4].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_salesOrder_table())
                toplevel.destroy()

        def onSaleNoEntry(*args, **kwargs):
            #print(f"{toplevel.stringVar[0].get() = }\n{toplevel.entries[0].cget('values') = }")
            if toplevel.stringVar[0].get() in toplevel.entries[0].cget("values"):
                toplevel.entries[1].configure(state="enabled", values=[f"{value[0]} - {value[1]}" for value in products])
                scrolledFrame.load_table(toplevel.stringVar[0].get())
            else:
                toplevel.entries[1].configure(state="readonly", foreground=self.styleObj.colors.get('secondary'), values = [])
                toplevel.stringVar[1].set('1 - Product Name')
                scrolledFrame.unload_table()

        def onProductEntry(*args, **kwargs):
            if toplevel.stringVar[1].get() in toplevel.entries[1].cget("values"):
                #print(f"{products = }\n {toplevel.stringVar[0].get().split(' - ')[0] = }")
                value = [value[2] for value in products if str(value[0]) == toplevel.stringVar[1].get().split(' - ')[0]]
                #print(f"{value = }")
                toplevel.stringVar[2].set(value[0])
                toplevel.entries[3].configure(to=1000)
                for i in [2,3]:
                    toplevel.entries[i].configure(state="enabled", foreground="black")
            else:
                #print("invalid")
                toplevel.stringVar[2].set("The chair, a silent sentinel, bore witness to the passage of time.")
                toplevel.stringVar[3].set("0")
                toplevel.entries[3].configure(to=0)
                for i in [2,3]:
                    toplevel.entries[i].configure(state="readonly", foreground=self.styleObj.colors.get("secondary"))
        def quantityEntryValidation(event):
            if float(toplevel.stringVar[3].get()) < 0 or float(toplevel.stringVar[3].get())>float(toplevel.entries[3].cget("to")):
                toplevel.errVar[3].set("Invalid Quantity Selected")
                return False
            try:
                int(toplevel.stringVar[3].get())
            except:
                toplevel.errVar[3].set("Only integers allowed")
                return False
            toplevel.errVar[3].set("")
            return True

        def generateSaleNoButton():
            self.db_connection.create_salesOrder()
            toplevel.entries[0].configure(values=self.db_connection.query_newSalesOrder())

        products = self.db_connection.query_product()

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Add Sales Order", entryFieldQty=5)

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Add Sales Order")
        for index, key in enumerate(["Sale No.", "Product No.", "Product Description", "Quantity"]):
            toplevel.create_label(frame=toplevel.frameList[index+1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index+1], errVar=toplevel.errVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], options=self.db_connection.query_newSalesOrder())
        toplevel.create_combobox(frame=toplevel.frameList[2], stringVar=toplevel.stringVar[1], state='readonly')
        toplevel.create_entry(frame=toplevel.frameList[3], stringVar=toplevel.stringVar[2], state="readonly")
        toplevel.create_spinbox(frame=toplevel.frameList[4], stringVar=toplevel.stringVar[3], to=0, state="readonly")
        scrolledFrame = saleDetailFrame(toplevel.frameList[5])
        toplevel.create_buttonbox(frame=toplevel.frameList[6])
        saleButton = ttk.Button(toplevel.frameList[6], bootstyle="dark", text="Generate new Sale No.", command= lambda: generateSaleNoButton())
        saleButton.grid(row=1, column=0, sticky="w")
        toplevel.submitButton.configure(command = lambda: onSubmitButton())



        # Preview Text
        entryList =["saleNoEntry", "productIDNameEntry", "productDescriptionEntry", "0Entry"]
        for index, value in enumerate(entryList):
            previewText(toplevel.entries[index], key=value)

        toplevel.stringVar[0].trace("w", onSaleNoEntry)
        toplevel.stringVar[1].trace("w", onProductEntry)

        # Validation
        add_validation(toplevel.entries[3], validator(quantityEntryValidation))

        # Bindings
        #toplevel.bind_entry_return()
        #toplevel.traceButton()
        def validateButton():
            #®print('aa')
            for index, value in enumerate(toplevel.entries):
                if str(toplevel.entries[index].cget("foreground")) == str(self.styleObj.colors.get("secondary")) or toplevel.stringVar[index].get() == "":
                    #print(f"Index {index}: {toplevel.entries[index].cget('foreground')}")
                    toplevel.submitButton.configure(state="disabled")
                    return True
            toplevel.submitButton.configure(state="enabled")
            return False

        for entry in toplevel.entries:
            #print(f"Entry Traced: {entry}")
            entry.bind("<FocusOut>", lambda event: validateButton(), add="+")
            entry.bind("<KeyRelease>", lambda event: validateButton(), add="+")
            entry.bind("<ButtonRelease>", lambda event: validateButton(), add="+")

        # Configure Frames
        for index in range (1, 5):
            toplevel.configure_frame(frame=toplevel.frameList[index])

        # Grid Frames
        toplevel.configure_toplevel()

    def updatePopup(self):
        '''UPDATE SALES DETAILS TABLE'''
        try:
            rowDetails = self.tableview.get_row(iid=self.tableview.view.focus()).values
        except:
            rowDetails = []

        def onSubmitButton():
            if not self.db_connection.update_salesOrder(toplevel.stringVar[0].get(), toplevel.stringVar[1].get().split(' -')[0],
                            toplevel.stringVar[2].get().split(' (')[0], toplevel.stringVar[3].get()):
                toplevel.errVar[3].set("Submission failed to process")
            else:
                self._load_table_rows(self.db_connection.query_salesOrder_table())
                toplevel.destroy()

        def onSaleNoEntry(*args, **kwargs):
            # print(f"{toplevel.stringVar[0].get() = }\n{toplevel.entries[0].cget('values') = }")
            if toplevel.stringVar[0].get() in toplevel.entries[0].cget("values"):
                toplevel.entries[1].configure(state="enabled", values=self.db_connection.query_salesorder_product(toplevel.stringVar[0].get()))
                toplevel.scrolledFrame.load_table(toplevel.stringVar[0].get())

            else:
                toplevel.entries[1].configure(state="readonly", foreground=self.styleObj.colors.get("secondary"), values=[])
                toplevel.stringVar[1].set("FUR-SOF-L-GR-001 - Product Name")
                toplevel.scrolledFrame.unload_table()

        def onProductNoEntry(*args, **kwargs):
            if toplevel.stringVar[1].get() in toplevel.entries[1].cget("values"):
                toplevel.entries[2].configure(state="enabled", values=self.db_connection.query_salesOrder_productBatch(toplevel.stringVar[1].get().split(' -')[0]))
            else:
                toplevel.entries[2].configure(state="readonly", foreground=self.styleObj.colors.get("secondary"), values=[])
                toplevel.stringVar[2].set("BATCH-YYMMDD-[A-Z]")

        def onBatchNoEntry(*args, **kwargs):
            #print(f"Function called.\n{toplevel.stringVar[2].get()}\n{toplevel.entries[2].cget('values')}\n")
            if toplevel.stringVar[2].get() in toplevel.entries[2].cget("values"):
                try:
                    num1 = re.search(r"\([\d]+", toplevel.stringVar[1].get()).group()[1:]
                    num2 = re.search(r"\([\d]+", toplevel.stringVar[2].get()).group()[1:]
                    qty = min(int(num1), int(num2))
                    print(f"{num1 = }\n{num2 = }\n{qty = }")
                    toplevel.entries[3].configure(state="enabled", to=qty)
                except Exception as err:
                    print(f"Lord spare my soul\n{err}")
            else:
                toplevel.entries[3].configure(state="readonly", foreground=self.styleObj.colors.get("secondary"), to=0)
                toplevel.stringVar[3].set("0")

        def onQuantityEntry(*args, **kwargs):
            qty = toplevel.stringVar[3].get()
            try:
                if 0 < int(qty) <= toplevel.entries[3].cget('to'):
                    toplevel.submitButton.configure(state='enabled')
            except:
                toplevel.submitButton.configure(state='disabled')



        # Creates Popup
        toplevel = salesPopup(parent=self.masterWindow, title="Update Sales Order")

        # Creates Widgets
        for index, key in enumerate(["Sales No.", "Product No.", "Product Batch", "Quantity"]):
            toplevel.create_label(frame=toplevel.frameList[index+1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index+1], errVar=toplevel.errVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], options=self.db_connection.query_updatableSalesOrder())
        toplevel.create_combobox(frame=toplevel.frameList[2], stringVar=toplevel.stringVar[1], state="readonly")
        toplevel.create_combobox(frame=toplevel.frameList[3], stringVar=toplevel.stringVar[2], state="readonly")
        toplevel.create_spinbox(frame=toplevel.frameList[4], stringVar=toplevel.stringVar[3], to=0, state="readonly")
        saleButton = ttk.Button(toplevel.frameList[6], bootstyle="dark", text="Update Selected Sale Inventory No.")
        #saleButton.grid(row=1, column=0, sticky="w")
        toplevel.submitButton.configure(command=lambda: onSubmitButton())

        # Preview Text
        entryList =["saleNoEntry", "inventoryProductEntry", "productBatchEntry", "quantityEntry"]
        for index, key in enumerate(entryList):
            previewText(toplevel.entries[index], key=key)

        toplevel.stringVar[0].trace("w", lambda x, y, z: onSaleNoEntry())
        toplevel.stringVar[1].trace("w", lambda x, y, z: onProductNoEntry())
        toplevel.stringVar[2].trace("w", lambda x, y, z: onBatchNoEntry())
        toplevel.stringVar[3].trace("w", lambda x, y, z: onQuantityEntry())

    def deletePopup(self):
        rowDetails = popup.getTableRows(self.tableview)
        if rowDetails == []:
            return
        if popup.deleteDialog(self) == "OK":
            if self.db_connection.delete_salesOrder(rowDetails[0]):
                self._load_table_rows(self.db_connection.query_salesOrder_table())
            else:
                popup.deleteFail(self)



    def validatePopup(self):
        try:
            rowDetails = self.tableview.get_row(iid=self.tableview.view.focus()).values
        except:
            rowDetails = []

        saleDetails = [list(value) for value in self.db_connection.query_salesOrder_validatable()]
        for value in saleDetails:
            value[2] = f"{value[2]:,}"
        #print(saleDetails)

        def onSubmitButton():
            if toplevel.stringVar[0].get().split('(')[1] == "Not Paid)":
                if not self.db_connection.validate_salesOrder(toplevel.stringVar[0].get()):
                    toplevel.errVar[4].set("Submission failed to process")
                else:
                    self._load_table_rows(self.db_connection.query_salesOrder_table())
                    toplevel.destroy()
            else:
                if not self.db_connection.update_salesOrder_delivery(toplevel.stringVar[0].get().split(' (')[0]):
                    toplevel.errVar[4].set("Submission failed to process")
                else:
                    self._load_table_rows(self.db_connection.query_salesOrder_table())
                    toplevel.destroy()

        def onSaleNoEntry(*args, **kwargs):
            #print("Function called.")
            #print(f"{toplevel.stringVar[0].get().split(' (')[0] = }")
            try:
                if toplevel.stringVar[0].get() in toplevel.entries[0].cget("values"):
                    #print(f"{toplevel.stringVar[0].get() = }\n{saleDetails = }")
                    details = [value[1:3] for value in saleDetails if value[0] == toplevel.stringVar[0].get().split(' (')[0]]
                    #print(f"{details = }")
                    for index, key in enumerate(*details):
                        toplevel.stringVar[index + 1].set(key)
                        toplevel.entries[index+1].configure(foreground="black")
                    #print(f"{toplevel.stringVar[0].get().split(' (')[0] = }")
                    scrolledFrame.load_table(f"{toplevel.stringVar[0].get().split(' (')[0]}")
                    toplevel.submitButton.configure(state="enabled")
                    #print(f"{saleDetails[-1] = }\n{saleDetails[-1].split('(') = }\n{saleDetails[-1].split('(')[1] = }")
                    if toplevel.stringVar[0].get().split('(')[1] == "Not Paid)":
                        toplevel.submitButton.configure(text="Validate Payment")
                    elif toplevel.stringVar[0].get().split('(')[1] == "Not Delivered)":
                        toplevel.submitButton.configure(text="Validate Delivery")
                else:
                    toplevel.stringVar[1].set("YYYY-MM-DD")
                    toplevel.stringVar[2].set("29.99")
                    for i in [1, 2]:
                        toplevel.entries[i].configure(foreground=self.styleObj.colors.get("secondary"))
                    scrolledFrame.unload_table()
                    toplevel.submitButton.configure(state="disabled", text="Submit")
            except Exception as err:
                print(f"Error: {err}")
                toplevel.stringVar[1].set("YYYY-MM-DD")
                toplevel.stringVar[2].set("29.99")
                for i in [1,2]:
                    toplevel.entries[i].configure(foreground=self.styleObj.colors.get("secondary"))
                scrolledFrame.unload_table()
                toplevel.submitButton.configure(state="disabled", text="Submit")


        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Validate Sales Order", entryFieldQty=4)

        # Creates Widgets
        toplevel.create_title_frame(frame=toplevel.frameList[0], title="Validate Sales Order")
        for index, key in enumerate(["Sales No", "Date Created", "Total Price"]):
            toplevel.create_label(frame=toplevel.frameList[index + 1], label=key)
            toplevel.create_errMsg(frame=toplevel.frameList[index + 1], errVar=toplevel.errVar[index])
        toplevel.create_combobox(frame=toplevel.frameList[1], stringVar=toplevel.stringVar[0], state="enabled", options = [f"{value[0]} ({value[-1]})" for value in saleDetails if value[-1]!="Delivered"])
        toplevel.create_entry(frame=toplevel.frameList[2], stringVar=toplevel.stringVar[1], state="readonly")
        toplevel.create_entry(frame=toplevel.frameList[3], stringVar=toplevel.stringVar[2], state="readonly")
        toplevel.create_buttonbox(frame=toplevel.frameList[5])
        toplevel.submitButton.configure(command= lambda: onSubmitButton())
        #print(f"{toplevel.frameList[5].winfo_children()[2].cget('textvariable') = }\n{toplevel.errVar[4].get() = }")
        toplevel.frameList[5].winfo_children()[2].configure(textvariable=toplevel.errVar[4])

        # Preview Text
        entryList = ["saleNoEntry", "dateEntry", "priceEntry"]
        for index, key in enumerate(entryList):
            previewText(toplevel.entries[index], key=key)

        toplevel.stringVar[0].trace("w", onSaleNoEntry)

        # Sale Details Frame
        scrolledFrame = saleDetailFrame(toplevel.frameList[4])

        if rowDetails != []:
            #print(rowDetails)
            toplevel.stringVar[0].set(f"{rowDetails[0]} ({rowDetails[-1]})")
            toplevel.entries[0].configure(foreground="black")
            onSaleNoEntry()

        # Configure Frames
        for index in [1, 2, 3]:
            toplevel.configure_frame(frame=toplevel.frameList[index])
        toplevel.rowconfigure(4, weight=1)

        # Grid Frames
        toplevel.configure_toplevel()


class salesPopup(popup):
    def __init__(self, parent:ttk.TTK_WIDGETS, title:str):
        super().__init__(master=parent, title=title, entryFieldQty=5)
        self.create_title_frame(self.frameList[0], title)
        self.scrolledFrame = saleDetailFrame(self.frameList[5])
        self.create_buttonbox(self.frameList[6])
        self.frameList[6].winfo_children()[2].configure(textvariable=self.errVar[4])
        for index in [1, 2, 3, 4]:
            self.configure_frame(frame=self.frameList[index])
        self.rowconfigure(5, weight=1)
        self.configure_toplevel()


class saleDetailFrame(ttk.Frame):
    def __init__(self, parent: ttk.TTK_WIDGETS):
        self.master = parent
        self.styleObj = ttk.style.Style.get_instance()
        self.db_connection = DatabaseConnection()
        self.counter = 1

        super().__init__(master=parent, bootstyle="danger", padding=0)
        self.grid(row=0, column=0, sticky="nwes")

        label = ttk.Label(self, text="Sale Details")
        label.grid(row=0, column=0, sticky="nwes")
        scrolledFrame = ttkbootstrap.scrolled.ScrolledFrame(self, padding=0, bootstyle="secondary-round", autohide=True)
        scrolledFrame.grid(row=1, column=0, sticky="nwes")
        #print(scrolledFrame["style"])

        self.tableview = ttkbootstrap.tableview.Tableview(master=scrolledFrame, stripecolor=(self.styleObj.theme.colors.get("light"), None), bootstyle="danger", autofit=True)
        self.tableview.grid(row=0, column=0, sticky="nwes")
        for header in ("No.", "Product Name", "Batch No", "Unit Price", "Quantity", "Total Price"):
            self.tableview.insert_column(index="end", text=header, anchor="center", stretch=False)

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        scrolledFrame.rowconfigure(0, weight=1)
        scrolledFrame.columnconfigure(0, weight=1)

    def load_table(self, saleNo: str):
        #print("Table Generated")
        #print(saleNo)
        self.tableview.delete_rows()
        for row in self.db_connection.query_saleDetails_table(saleNo):
            #print(row)
            self.tableview.insert_row('end', [f"{self.counter}."] + list(row))
            self.counter += 1
        self.counter=1
        self.tableview.load_table_data()

    def unload_table(self):
        #print("Table Unloaded")
        self.tableview.unload_table_data()

    def __generate_summary_row__(self):
        pass





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
    rFrame = salesOrderFrame(window, "Administrator", 1)
    lFrame = navigationFrame(window, employeeID=1, rFrame=rFrame)
    #rFrame.validatePopup()
    #rFrame.createPopup()

    # Starts Event Main Loop
    window.mainloop()