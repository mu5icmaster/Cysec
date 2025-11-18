from Frames.pageFrame import *
from Database.Database import DatabaseConnection
import re
from Frames.popup import popup
from ttkbootstrap.dialogs import Messagebox


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

    def _validate_vendor_form(self, tl) -> bool:
        """
        tl: add/update Pop-up object popup(...)
        Sequence：
          0: Vendor ID (Read)
          1: Vendor Name
          2: Email
          3: Contact Number
        """
        name    = tl.stringVar[1].get().strip()
        email   = tl.stringVar[2].get().strip()
        contact = tl.stringVar[3].get().strip()

        errors = []

    # Align with your utils.validation rules 
        if not name or re.search(r"[^a-zA-Z0-9_\s\-,.']", name):
            errors.append("Invalid Vendor Name.")

        if not re.match(r"^[\w\-.]+@([\w-]+\.)+[\w-]{2,}$", email):
            errors.append("Invalid Email Format.")

    # `contactNumber` validation is a 10-digit number.
        if not re.match(r"^[\d]{10}$", contact):
            errors.append("Invalid Contact Number (must be 10 digits).")

        if errors:
        # Sync to red text prompt
            if "Invalid Vendor Name." in errors:
                tl.errVar[1].set("Only alphanumeric characters allowed.")
            if "Invalid Email Format." in errors:
                tl.errVar[2].set("Invalid Email Format")
            if any("Contact Number" in e for e in errors):
                tl.errVar[3].set("Invalid Contact Number")

        # Pop-up window prevents submission
            Messagebox.show_error("\n".join(errors), "Validation Error", parent=tl)
            return False

    # 全部通过，清掉红字
        tl.errVar[1].set("")
        tl.errVar[2].set("")
        tl.errVar[3].set("")
        return True

    def addPopup(self):

        # Creates Popup
        toplevel = popup(master=self.masterWindow, title="Add Vendor", entryFieldQty=4)

        def onButtonPress():
    # 后端强制校验（最后一道闸）
            if not self._validate_vendor_form(toplevel):
                return

            try:
                ok = self.db_connection.add_vendor(
                    toplevel.stringVar[1].get().strip(),
                    toplevel.stringVar[2].get().strip(),
                    toplevel.stringVar[3].get().strip()
                )
                if not ok:
                    toplevel.errVar[3].set("Submission failed to process")
                    Messagebox.show_error("Create vendor failed.", "Database", parent=toplevel)
                    return
                
                self.db_connection.log_event(
                    actor_id=self.employeeID,
                    actor_name=self.name if hasattr(self, "name") else str(self.employeeID),
                    action="CREATE_VENDOR",
                    target_type="Vendor",
                    target_id=toplevel.stringVar[0].get(),  # Vendor ID
                    detail=f"name={toplevel.stringVar[1].get()}, email={toplevel.stringVar[2].get()}"
                )    

                self._load_table_rows(self.db_connection.query_vendor_all())
                toplevel.destroy()
            except Exception as e:
                toplevel.errVar[3].set("Submission failed to process")
                Messagebox.show_error(f"Database error:\n{e}", "Database", parent=toplevel)



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
    # 提交前强制校验
            if not self._validate_vendor_form(toplevel):
                return

            try:
        # 你原本参数顺序是 (VendorID, VendorName, Contact, Email)
                params = []
                for i in [0, 1, 3, 2]:
                    params.append(toplevel.stringVar[i].get().strip())

                ok = self.db_connection.update_vendor(*params)
                if not ok:
                    toplevel.errVar[4].set("Submission failed to process")
                    Messagebox.show_error("Update vendor failed.", "Database", parent=toplevel)
                    return
                
                self.db_connection.log_event(
                    actor_id=self.employeeID,
                    actor_name=self.name if hasattr(self, "name") else str(self.employeeID),
                    action="UPDATE_VENDOR",
                    target_type="Vendor",
                    target_id=toplevel.stringVar[0].get(),
                    detail=f"name={toplevel.stringVar[1].get()}, email={toplevel.stringVar[2].get()}"
                )

                self._load_table_rows(self.db_connection.query_vendor_all())
                toplevel.destroy()
            except Exception as e:
                toplevel.errVar[3].set("Submission failed to process")
                Messagebox.show_error(f"Database error:\n{e}", "Database", parent=toplevel)


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

                self.db_connection.log_event(
                    actor_id=self.employeeID,
                    actor_name=self.name if hasattr(self, "name") else str(self.employeeID),
                    action="DELETE_VENDOR",
                    target_type="Vendor",
                    target_id=rowDetails[0],  # 被删除的 Vendor ID
                    detail=""
                )
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