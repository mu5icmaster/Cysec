from Frames.pageFrame import *
from Database.Database import DatabaseConnection
from ttkbootstrap.validation import validator, add_validation
import ttkbootstrap as ttk
from Frames.popup import popup
from utils import previewText


class inventoryFrame(pageFrame):
    """
    Inventory page with Receive / Update / Delete actions.
    This version fixes Worker-side Update validation/submit and hardens comboboxes.
    """

    def __init__(self, master: ttk.Window, role: str, employeeID: int) -> None:
        super().__init__(master=master,
                         title="Inventory",
                         role=role,
                         button_config={
                             "Worker": ["Receive", "Update", "Delete"],
                             "Supervisor": ["Receive", "Update", "Delete"],
                             "Administrator": ["Receive", "Update", "Delete"]
                         },
                         employeeID=employeeID)

        self.db_connection = DatabaseConnection()

        # Table columns
        colNames = ["Inventory ID", "Product No", "Name", "Description", "Quantity", "Location", "Batch Number ID"]
        for name in colNames:
            self._insert_table_columns(name)

        self._load_table_rows(self.db_connection.query_inventory_table())

    def getButtonCommand(self, button_text):
        if button_text == "Receive":
            self.receivePopup()
        elif button_text == "Update":
            self.updatePopup()
        elif button_text == "Delete":
            self.deletePopup()

    # -------------------------
    # Receive Inventory
    # -------------------------
    def receivePopup(self):
        receivables = self.db_connection.query_purchaseOrder_receivables()
        shipmentIDs = [value[0] for value in receivables]

        def onShipmentSelect(*_):
            try:
                row = next(v for v in receivables if v[0] == top.stringVar[0].get())
            except StopIteration:
                row = ["", "", "", "", "", ""]
            # Expecting: [Shipment No, Product No, Product Name, Description, Quantity, Vendor]
            for i, val in enumerate(row[0:6]):
                top.stringVar[i].set(val)
                if i > 0:
                    top.entries[i].configure(state="readonly")

        def submit():
            try:
                ok = self.db_connection.update_purchaseOrder_receive(top.stringVar[0].get())
                if ok:
                    self._load_table_rows(self.db_connection.query_inventory_table())
                    popup.infoPopup(self, "Shipment received.")
                    top.destroy()
                else:
                    popup.infoPopup(self, "Failed to receive shipment.")
            except Exception as e:
                popup.infoPopup(self, f"Error: {e}")

        top = popup(master=self.masterWindow, title="Receive Inventory", entryFieldQty=6)
        top.create_title_frame(frame=top.frameList[0], title="Receive Inventory")

        labels = ["Shipment No", "Product No", "Product Name", "Product Description", "Quantity", "Vendor"]
        for idx, key in enumerate(labels):
            top.create_label(frame=top.frameList[idx+1], label=key)
            top.create_errMsg(frame=top.frameList[idx+1], errVar=top.errVar[idx])

        top.create_combobox(frame=top.frameList[1], stringVar=top.stringVar[0], options=shipmentIDs, state="readonly")
        for i in range(1, 6):
            top.create_entry(frame=top.frameList[i+1], stringVar=top.stringVar[i], state="readonly")

        top.create_button_frame()
        top.create_submitButton(command=submit)
        top.create_cancelButton(command=top.destroy)

        top.stringVar[0].trace("w", onShipmentSelect)
        previewText(top.entries[1], key="productNoEntry")
        previewText(top.entries[4], key="quantityEntry")

        for index in range(1, 7):
            top.configure_frame(frame=top.frameList[index])
        top.configure_toplevel()

    # -------------------------
    # Update Inventory (fixed)
    # -------------------------
    def updatePopup(self):
        """
        Move inventory between locations with strict validation.
        Works for Worker/Supervisor/Admin; comboboxes are read-only.
        """
        # Try to preselect from focused row
        try:
            rowDetails = self.tableview.get_row(iid=self.tableview.view.focus()).values
            if rowDetails[-2] == "Output":
                popup.infoPopup(self, "Row selected is already located at Output.")
                return
        except Exception:
            rowDetails = []

        updatables = self.db_connection.query_inventory_updatable()  # { "PRODNO - Name": "Description" }
        product_options = list(updatables.keys())

        # dynamic lists
        src_locations = []
        batches = []
        dest_locations = ["1 - Input", "2 - Warehouse", "3 - Packing Zone", "4 - Output"]

        def onProductChange(*_):
            # Update description, source locations, batches
            pname = top.stringVar[0].get()
            top.stringVar[1].set(updatables.get(pname, ""))

            # Source locations for selected product
            try:
                # Expected: ["1 - Input (qty: X)", "2 - Warehouse (qty: Y)", ...]
                src = self.db_connection.query_inventory_location(pname.split(' - ')[0])
            except Exception:
                src = []
            top.entries[2].configure(values=src, state="readonly")
            top.stringVar[2].set("")

            # Batches for this product; fallback to all batches if specific query missing
            try:
                batches_list = self.db_connection.query_inventory_productBatch(pname.split(' - ')[0])
            except Exception:
                try:
                    batches_list = self.db_connection.query_productBatchNo()
                except Exception:
                    batches_list = []
            top.entries[3].configure(values=batches_list, state="readonly")
            top.stringVar[3].set("")

        def onSrcChange(*_):
            top.entries[5].configure(values=dest_locations, state="readonly")

        def quantityValidation(event):
            txt = top.stringVar[4].get().strip()
            if not txt.isdigit() or int(txt) <= 0:
                top.errVar[4].set("Enter a positive number")
                return False
            top.errVar[4].set("")
            return True

        def destValidation(event):
            val = top.stringVar[5].get()
            options = list(top.entries[5].cget("values"))
            if val not in options:
                top.errVar[5].set("Invalid Warehouse Location")
                return False
            # forbid destination == source
            src = top.stringVar[2].get()
            if src and val.split(' - ')[0] == src.split(' - ')[0]:
                top.errVar[5].set("Source and destination cannot be the same")
                return False
            top.errVar[5].set("")
            return True

        def submit():
            # Validate again
            if not quantityValidation(None) or not destValidation(None):
                popup.infoPopup(self, "Please fix validation errors.")
                return
            try:
                product_no = top.stringVar[0].get().split(' - ')[0]
                batch_no = top.stringVar[3].get().split(' - ')[0] if ' - ' in top.stringVar[3].get() else top.stringVar[3].get()
                src_id = int(top.stringVar[2].get().split(' - ')[0])
                des_id = int(top.stringVar[5].get().split(' - ')[0])
                qty = int(top.stringVar[4].get())
            except Exception:
                popup.infoPopup(self, "Missing or invalid fields.")
                return
            try:
                ok = self.db_connection.update_inventory(product_no, batch_no, src_id, des_id, qty)
                if ok:
                    self._load_table_rows(self.db_connection.query_inventory_table())
                    popup.infoPopup(self, "Inventory updated.")
                    top.destroy()
                else:
                    popup.infoPopup(self, "Update failed.")
            except Exception as e:
                popup.infoPopup(self, f"Error: {e}")

        # --- Build popup ---
        top = popup(master=self.masterWindow, title="Update Inventory", entryFieldQty=6)
        top.create_title_frame(frame=top.frameList[0], title="Update Inventory")

        labels = ["Product No.", "Product Description", "Source Location",
                  "Product Batch No.", "Quantity", "Destination Location"]
        for idx, key in enumerate(labels):
            top.create_label(frame=top.frameList[idx+1], label=key)
            top.create_errMsg(frame=top.frameList[idx+1], errVar=top.errVar[idx])

        top.create_combobox(frame=top.frameList[1], stringVar=top.stringVar[0],
                            options=product_options, state="readonly")
        top.create_entry(frame=top.frameList[2], stringVar=top.stringVar[1], state="readonly")
        top.create_combobox(frame=top.frameList[3], stringVar=top.stringVar[2], options=src_locations, state="readonly")
        top.create_combobox(frame=top.frameList[4], stringVar=top.stringVar[3], options=batches, state="readonly")
        top.create_entry(frame=top.frameList[5], stringVar=top.stringVar[4])
        top.create_combobox(frame=top.frameList[6], stringVar=top.stringVar[5],
                            options=dest_locations, state="readonly")

        previewText(top.entries[1], key="productNoEntry")
        previewText(top.entries[5], key="quantityEntry")

        # Validation
        add_validation(top.entries[5], validator(quantityValidation), when="focus")
        add_validation(top.entries[6], validator(destValidation), when="focus")

        # Bindings
        top.stringVar[0].trace("w", onProductChange)
        top.stringVar[2].trace("w", onSrcChange)

        # Pre-fill with selected row if available
        if rowDetails:
            try:
                # rowDetails: ["Inventory ID","Product No","Name","Description","Quantity","Location","Batch Number ID"]
                p = f"{rowDetails[1]} - {rowDetails[2]}"
                if p in product_options:
                    top.stringVar[0].set(p)
                else:
                    top.stringVar[0].set("")
                # options for src/batch will populate via onProductChange
            except Exception:
                pass

        top.create_button_frame()
        top.create_submitButton(command=submit)
        top.create_cancelButton(command=top.destroy)

        for index in range(1, 7):
            top.configure_frame(frame=top.frameList[index])
        top.configure_toplevel()

    # -------------------------
    # Delete Inventory
    # -------------------------
    def deletePopup(self):
        try:
            row = self.tableview.get_row(iid=self.tableview.view.focus()).values
        except Exception:
            popup.infoPopup(self, "Please select an inventory row to delete.")
            return

        inv_id = row[0]

        def submit():
            try:
                ok = self.db_connection.delete_inventory(int(inv_id))
                if ok:
                    self._load_table_rows(self.db_connection.query_inventory_table())
                    popup.infoPopup(self, "Inventory deleted.")
                    top.destroy()
                else:
                    popup.infoPopup(self, "Delete failed.")
            except Exception as e:
                popup.infoPopup(self, f"Error: {e}")

        top = popup(master=self.masterWindow, title="Delete Inventory", entryFieldQty=1)
        top.create_title_frame(frame=top.frameList[0], title="Delete Inventory")
        top.create_label(frame=top.frameList[1], label=f"Delete Inventory ID: {inv_id}?")
        top.create_button_frame()
        top.create_submitButton(text="Delete", bootstyle="danger", command=submit)
        top.create_cancelButton(command=top.destroy)
        top.configure_frame(frame=top.frameList[1])
        top.configure_toplevel()


if __name__ == '__main__':
    # Dev harness: show just the inventory frame
    from navigationFrame import navigationFrame
    window = ttk.Window(title="Keai IWMS", themename="litera", size=(1280, 720))
    ttk.window.Window.place_window_center(window)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=20)

    rFrame = inventoryFrame(window, "Worker", employeeID=3)
    lFrame = navigationFrame(window, 3, rFrame)
    window.mainloop()
