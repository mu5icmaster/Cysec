import re
import sqlite3
import os
from datetime import date, datetime
from loguru import logger
import json
from ttkbootstrap.toast import ToastNotification

from configuration import Configuration
from utils_otp import now, MAX_ATTEMPTS



def singleton(cls):
    """Decorator to create a singleton class."""
    instances = {}

    def wrapper(*args, **kwargs):
        #print(f"wrapper started for {cls}")
        if cls not in instances:
            #print("no instance found")
            instances[cls] = cls(*args, **kwargs)
        #print(f"Returning this instance: {str(instances[cls])}" )
        return instances[cls]

    return wrapper


@singleton
class DatabaseConnection:
    # ---- RBAC helpers -------------------------------------------------
    def _role_of(self, employee_id: int) -> str:
        """Return the role name for a worker id, or '' if not found."""
        try:
            self.cursor.execute("""
                SELECT r.RoleName
                FROM Workers w
                JOIN Roles r ON w.RoleID = r.RoleID
                WHERE w.WorkerID = ?
            """, (int(employee_id),))
            row = self.cursor.fetchone()
            return row[0] if row else ""
        except Exception:
            return ""

    def _require_role(self, employee_id: int | None, allowed: tuple[str, ...]):
        """Raise PermissionError if employee_id is not in an allowed role.
        If employee_id is None, allow (back-compat)."""
        if employee_id is None:
            return
        role = self._role_of(employee_id)
        if role not in allowed:
            raise PermissionError(f"Role '{role}' not permitted for this action.")

    def _log_user_activity(self, employee_id: int | None, message: str):
        """Log to your existing 'User Activities' stream if available."""
        try:
            if hasattr(self, "logger"):
                self.logger.info(message, type="report", key="User Activities")
        except Exception:
            pass
    # -------------------------------------------------------------------


    def __init__(self):
        self.config = Configuration()
        db_filepath = self.config.getDatabaseFile()
        #print(f"DatabaseConnection Constructor-> Database File Path\n{db_filepath}")

        if not os.path.exists(db_filepath):
            self.connection = sqlite3.connect(db_filepath)
            self.cursor = self.connection.cursor()
            self._create_tables()
            self.connection.commit()

        else:
            self.connection = sqlite3.connect(db_filepath)
            self.cursor = self.connection.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.connection.commit()

        logger.add(f"{self.config.getLogFile()}", retention="3 months",
                   filter=self.log_notification_filter,
                   format="{time:YYYY-MM-DD HH:mm:ss} | {extra[event]} Event | Employee ID: {extra[id]} | {level}")
        logger.add(f"{self.config.getLogFile()}", retention="3 months",
                   filter=self.log_report_filter,
                   format="""{time:YYYY-MM-DD HH:mm:ss} | {extra[key]} Report | Employee ID: {extra[id]} | {message} | {level}""")
        self.logger = logger.bind(id='1', placeholder="", type="notification")
        self.employeeID = 1

<<<<<<< HEAD
=======
        # === ensure OTP table exists ===
        self._ensure_otp_table()


>>>>>>> dfcd0630c26e219a7187e71cd49a3531ad29663d
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def log_notification_filter(self, record):
        if record["extra"]["type"] == "notification":
            self.create_notification(record["extra"]["event"], record["extra"]["placeholder"])
            return True

        else:
            return False

    def log_report_filter(self, record):
        if record["extra"]["type"] == "report":
            return True

        else:
            return False

    def log_employee(self, employee_id):
        """
        1. Create a logger, and log the employee ID when login occurs
        2. Bind the employee ID to the DatabaseConnection Class
        3. Modify functions to write notifications to database as logs are written
        4. Parse logs to aggregate log information for graphs for GUI
        """
        self.logger = logger.bind(id=str(employee_id), placeholder="")
        self.employeeID = employee_id
        self.logger.success(f"Successfully authenticated (Employee ID: {employee_id})", event="Authentication",
                            placeholder="xxx", type="notification")

    def query_product_movement_report(self):
        pattern = r"(?P<time>\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2} \| " \
                  r"Product Movement Report \| Employee ID: (?P<employee_id>[0-9]+) \| " \
                  r"(?P<msg>[\w\s\|-]+) \| INFO"
        results = []
        for e in logger.parse(f"{self.config.getLogFile()}", pattern=pattern):
            results.append([e["time"]] + e["msg"].split(' | ') + ["Done"])
        return results

    def query_stock_level_report(self) -> list[list[str]]:
        """Returns: ["Product", "Unit Cost", "Total Value", "On Hand", "Free to Use", "Incoming", "Outgoing"]"""
        try:
            self.cursor.execute("""
            WITH AvailableStock AS (SELECT p.ProductID,
            COALESCE(SUM(CASE WHEN i.LocationID != 5 THEN i.StockQuantity ELSE 0 END), 0) AS TotalStock
            FROM Products p LEFT JOIN Inventory i ON p.ProductID = i.ProductID GROUP BY p.ProductID),
            
            UndeliveredSales AS (SELECT p.ProductID,
            SUM(CASE WHEN ss.Status != 'Delivered' THEN si.QuantitySold ELSE 0 END) AS UndeliveredQuantity
            FROM Products p LEFT JOIN Sales_Inventory si ON p.ProductID = si.ProductID
            LEFT JOIN Sales ss ON si.SaleID = ss.SaleID GROUP BY p.ProductID)
            
            SELECT p.ProductName, p.Price, av.TotalStock * p.Price, av.TotalStock,
            av.TotalStock - us.UndeliveredQuantity,
            COALESCE(SUM(CASE WHEN s.Status != 'Received' THEN s.Quantity ELSE 0 END), 0), us.UndeliveredQuantity
            
            FROM Products p LEFT JOIN Inventory i ON p.ProductID = i.ProductID
            LEFT JOIN Shipments s ON p.ProductID = s.ProductID
            LEFT JOIN AvailableStock av ON p.ProductID = av.ProductID
            LEFT JOIN UndeliveredSales us ON p.ProductID = us.ProductID
            GROUP BY p.ProductID
            """)
            results = [list(value) for value in self.cursor.fetchall()]
            for value in results:
                value[2] = f"{round(float(value[2]), 2):.2f}"
            return results

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_employee_report(self, employee_id: int | str):
        """Returns: [Employee ID - Employee Name, Role Name, Email, Contact Number,
        Total Tasks Assigned, Total Tasks Completed, Total Tasks Overdue]"""

        try:
            self.cursor.execute("""SELECT w.WorkerID || ' - ' || w.Name, r.RoleName, a.Email, w.ContactNumber,
            COALESCE(COUNT(t.TaskID), 0), COALESCE(COUNT(CASE WHEN t.TaskStatus = 'Completed' THEN 1 END), 0),
            COALESCE(COUNT(CASE WHEN t.TaskStatus != 'Completed' THEN 1 END), 0)
            FROM Workers w INNER JOIN Roles r ON w.RoleID = r.RoleID
            INNER JOIN Accounts a ON w.WorkerID = a.WorkerID
            LEFT JOIN Tasks t ON w.WorkerID = t.WorkerID
            WHERE w.WorkerID = ?
            GROUP BY w.WorkerID
            """, (employee_id,))
            return self.cursor.fetchone()

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_traceability_report(self, batch_no: str, product_name: str = None) -> list[str]:
        """Returns: ["Employee ID - Employee Name", "Product No - Product Name", "Date", "Batch No.", "From", "To",
        Quantity]"""
        pattern = r"(?P<time>\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2} \| " \
                  r"Product Movement Report \| Employee ID: (?P<employee_id>[0-9]+) \| " \
                  r"(?P<msg>[\w\s\|-]+) \| INFO"
        results = []
        for e in logger.parse(f"{self.config.getLogFile()}", pattern=pattern):
            data = [e["employee_id"]] + e["msg"].split(' | ')
            if data[2] == batch_no and data[1] == product_name:
                data.insert(2, e["time"])
                results.append(data)
        try:
            self.cursor.execute("""SELECT w.WorkerID || ' - ' || w.Name FROM Workers w""")
            workers = [value[0] for value in self.cursor.fetchall()]
            self.cursor.execute("""SELECT p.ProductNo || ' - ' || p.ProductName FROM Products p""")
            products = [value[0] for value in self.cursor.fetchall()]
            for i, result in enumerate(results):
                result[0] = [value for value in workers if value.split(' - ')[0] == result[0]][0]
                result[1] = [value for value in products if value.split(' - ')[1] == result[1]][0]
            return results

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_user_activities_report(self) -> list[list[str]]:
        """Returns: [Date, Time, User, Activity, Remark]"""
        pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \| " \
                  r"User Activities Report \| Employee ID: (?P<employee_id>[0-9]+) \| " \
                  r"(?P<msg>[\w\s\|-]+) \| INFO"
        results = []
        self.cursor.execute("""SELECT w.WorkerID || ' - ' || w.Name FROM Workers w""")
        worker_names = [value[0] for value in self.cursor.fetchall()]
        for e in logger.parse(f"{self.config.getLogFile()}", pattern=pattern):
            name = [value.split(' - ')[1] for value in worker_names if value.split(' - ')[0] == e["employee_id"]][0]
            time = datetime.strptime(e["time"], "%H:%M:%S").strftime("%I:%M:%S %p")
            results.append([e["date"], time, name, *e["msg"].split(' | ')])
        return results

    def create_notification(self, notification_key: str, placeholder: str = None):
        """Creates a new notification. Placeholder is inserted if necessary."""
        with open(f"{self.config.repo_file_path}/Database/Notifications.json", "r") as f:
            try:
                data = json.load(f)[notification_key]
            except KeyError:
                return

        if placeholder is not None:
            data["Message"] = data["Message"].format(placeholder)

        self.add_notification(data["Access"], data["Message"])

        dictionary = {"Worker": 3, "Supervisor": 2, "Administrator": 1}
        if dictionary[self.query_employee(self.employeeID)[1]] <= dictionary[(data["Access"])]:
            ToastNotification(title=data["Title"], message=data["Message"], duration=500).show_toast()

    def query_accounts_table(self) -> tuple:
        self.cursor.execute("""SELECT w.WorkerID, w.Name, r.RoleName, a.Email, w.ContactNumber
                FROM Workers w INNER JOIN Roles r ON w.RoleID=r.RoleID
                INNER JOIN Accounts a ON w.WorkerID=a.WorkerID """)
        return tuple(self.cursor.fetchall())

    def query_employee(self, employeeID: int) -> tuple:
        """Returns: [EmployeeName: str, RoleName: str]"""
        self.cursor.execute("""SELECT w.Name, r.RoleName, a.Email 
                FROM Roles r INNER JOIN Workers w ON w.RoleID = r.RoleID 
                INNER JOIN Accounts a ON w.WorkerID = a.WorkerID
                WHERE w.WorkerID = ?""",
                            (employeeID,))
        return self.cursor.fetchone()

    def query_employee_login(self, email: str) -> int:
        """Returns employee ID"""
        self.cursor.execute("""SELECT w.WorkerID FROM Workers w
        INNER JOIN Accounts a ON w.WorkerID = a.WorkerID WHERE a.Email = ?""", (email,))

        return self.cursor.fetchone()[0]

    def query_worker(self) -> list[str]:
        """Returns: ['WorkerID - Name', ...] (all roles)"""
        try:
            self.cursor.execute("""
                SELECT w.WorkerID || ' - ' || w.Name
                FROM Workers w
                ORDER BY w.Name
            """)
            return [row[0] for row in self.cursor.fetchall()]
        except Exception:
            return []

    def query_notification(self, role: str) -> list:
        try:
            self.cursor.execute("""SELECT RoleID From Roles WHERE RoleName = ?""", (role,))
            roleID = self.cursor.fetchone()[0]
            notifications = []

            for index in range(3, roleID - 1, -1):
                self.cursor.execute("""SELECT NotificationID, TimeStamp, NotificationDesc FROM Notification 
                                    WHERE RoleID = ?""", (index,))
                notifications += self.cursor.fetchall()

            notifications = sorted(notifications, key=lambda row: row[1], reverse=True)
            return notifications

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def add_notification(self, role: str, message: str) -> int:
        try:
            self.cursor.execute("""SELECT RoleID From Roles WHERE RoleName = ?""", (role,))
            roleID = self.cursor.fetchone()[0]
            self.cursor.execute("""INSERT INTO Notification (RoleID, Timestamp, NotificationDesc)
                VALUES (?, ?, ?)""", (roleID, datetime.now(), message,))
            self.connection.commit()

            return self.cursor.lastrowid

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return -1

    def delete_notification(self, notificationID: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM Notification WHERE NotificationID = ?", (notificationID,))
            self.connection.commit()
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_productBatch_today(self) -> list:
        try:
            values = self.cursor.execute("SELECT PBatchNumber FROM Product_Batch")
            latest = [value[0] for value in values if value[0].split('-')[1] == date.today().strftime("%y%m%d")]
            #print(latest)
            self.cursor.execute("SELECT PBatchNumber FROM Product_Batch ORDER BY PBatchID DESC LIMIT 1")
            try:
                latest += [self._generateID(self.cursor.fetchone()[0])]
            except TypeError:
                latest += [f"BATCH-{date.today().strftime('%y%m%d')}-A"]
            return latest

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_all_product_nos(self) -> list:
        """Returns a list of all product batch no."""
        try:
            self.cursor.execute("SELECT ProductNo FROM Products")
            return [i[0] for i in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []
    def query_productID(self, productName: str) -> str:
        try:
            self.cursor.execute("SELECT ProductID FROM Products WHERE ProductName = ?", (productName,))
            return f"{self.cursor.fetchone()[0]} - {productName}"

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return ""

    def query_productDescription(self, productID: int) -> str:
        try:
            self.cursor.execute("SELECT Description FROM Products WHERE ProductID = ?", (productID,))
            return self.cursor.fetchone()[0]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return ""

    def add_productBatch(self, batchnumber: str) -> bool:
        try:
            self.cursor.execute("INSERT INTO Product_Batch (PBatchNumber) VALUES (?)", (batchnumber,))
            self.connection.commit()
            self.logger.info(f"Create Product Batch No. | {batchnumber}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_product_table(self) -> list:
        """Returns: [ProductNo, Name, Description, Unit Price, Quantity, Preferred Vendor]"""
        try:
            self.cursor.execute("""SELECT ProductID, SUM(StockQuantity) 
            FROM Inventory WHERE LocationID != 5 GROUP BY ProductID ORDER BY ProductID""")
            quantityDict = {}
            for row in self.cursor.fetchall():
                quantityDict[row[0]] = row[1]
            self.cursor.execute("""
            SELECT p.ProductNo, p.ProductName, p.Description, p.Price, s.Name
            FROM Products p LEFT JOIN Suppliers s ON p.PreferredSupplierID = s.SupplierID
            ORDER BY p.ProductID
            """)
            queryList = self.cursor.fetchall()
            returnList = []
            for index, row in enumerate(queryList):
                try:
                    qty = [quantityDict[index + 1]]
                except:
                    qty = [0]
                tempList = list(row)[:4] + qty + list(row)[4:]
                returnList += [tempList]
            return returnList


        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_product(self) -> list:
        """Returns: [ProductID, ProductName, Description]"""
        try:
            self.cursor.execute("SELECT ProductID, ProductName, Description FROM Products")
            products = self.cursor.fetchall()
            return products
        except sqlite3.Error:
            return []

    def query_product_dashboard(self) -> list[str]:
        """Returns parameters for the dashboard product details frame widget."""
        try:
            result = []
            self.cursor.execute("""SELECT ProductID, COALESCE(SUM(StockQuantity), 0) 
            FROM Inventory WHERE LocationID !=5 GROUP BY ProductID""")
            result.append(len([value for value in self.cursor.fetchall() if int(value[1]) < 25]))
            # print(result)
            self.cursor.execute("""SELECT ProductNo FROM Products""")
            temp = []
            for value in self.cursor.fetchall():
                if value[0].split('-')[0] not in temp:
                    temp.append(value[0].split('-')[0])
            result.append(len(temp))
            # print(result)
            self.cursor.execute("""SELECT COUNT(ProductID) FROM Products""")
            result.append(self.cursor.fetchone()[0])
            # print(result)
            self.cursor.execute("""SELECT ProductID, COALESCE(SUM(StockQuantity), 0) 
            FROM Inventory WHERE LocationID !=5 GROUP BY ProductID""")
            result.append(len([value for value in self.cursor.fetchall() if int(value[1]) == 0]))
            return result

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return ['0', '0', '0', '0']

    def query_product_meter(self) -> list:
        """Returns parameters for the dashboard meter widget. [Product Types, Product Types in Inventory]"""
        try:
            results = []
            self.cursor.execute("SELECT COALESCE(COUNT(ProductID), 0) FROM Products")
            results.append(int(self.cursor.fetchone()[0]))
            self.cursor.execute("""SELECT COALESCE(COUNT(DISTINCT ProductID), 0) FROM Inventory WHERE LocationID!=5
            """)
            try:
                results.append(int(self.cursor.fetchone()[0]))
            except TypeError:
                results.append('0')
            return results

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return [0, 0]

    def query_product_popular(self) -> list:
        """Returns parameters for the dashboard top selling items frame widget."""
        try:  # Add Quantity Sold
            self.cursor.execute("""SELECT p.ProductNo, p.ProductName, SUM(i.QuantitySold)
            FROM Products p INNER JOIN Sales_Inventory i ON p.ProductID = i.ProductID
            INNER JOIN Sales s ON i.SaleID = s.SaleID
            WHERE s.Status = 'Delivered' 
            GROUP BY p.ProductID
            ORDER BY SUM(i.QuantitySold) DESC
            LIMIT 3
            """)
            return self.cursor.fetchall()

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def add_product(self, product_no: str, product_name: str, description: str, price: float,
                    preferred_supplier_id: int) -> bool:
        try:
            self.cursor.execute("""
                INSERT INTO Products (ProductNo, ProductName, Description, Price, PreferredSupplierID)
                VALUES (?, ?, ?, ?, ?)
                """, (product_no, product_name, description, price, preferred_supplier_id))
            self.connection.commit()
            self.logger.success("", event="New Product Added", placeholder=product_name, type="notification")
            self.logger.warning("", event="Out of Stock Alert", placeholder=product_name, type="notification")
            self.cursor.execute("""SELECT Name FROM Suppliers WHERE SupplierID = ?""", (preferred_supplier_id,))
            self.logger.info(
                f"Create New Product | {product_no} - {product_name} (RM{price}) [{self.cursor.fetchone()[0]}]",
                type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def update_product(self, product_no: str, product_name: str, description: str, price: float,
                       preferred_supplier_id: int) -> bool:
        try:
            self.cursor.execute("""SELECT ProductName, Description, Price, PreferredSupplierID FROM Products 
            WHERE ProductNo = ?""", (product_no,))
            old_values = [value for value in self.cursor.fetchone()]
            self.cursor.execute("""SELECT Name FROM Suppliers WHERE SupplierID = ?""", (old_values[3],))
            old_values[3] = self.cursor.fetchone()[0]
            self.cursor.execute("""
            UPDATE Products SET ProductName = ?, Description = ?, Price = ?, PreferredSupplierID = ? WHERE ProductNo = ?
            """, (product_name, description, price, preferred_supplier_id, product_no,))
            self.connection.commit()

            self.cursor.execute("""SELECT Name FROM Suppliers WHERE SupplierID = ?""", (preferred_supplier_id,))
            new_supplier_name = self.cursor.fetchone()[0]
            variables = [("Product Name", product_name), ("Product Description", description), ("Price", price),
                         ("Preferred Supplier", new_supplier_name)]

            for i, (var_name, var_value) in enumerate(variables):
                if old_values[i] != var_value:
                    self.logger.info(
                        f"Update Product | {product_no} - {product_name} {var_name}: {old_values[i]} -> {var_value}",
                        type="report", key="User Activities")

            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def delete_product(self, product_no: str) -> bool:
        try:
            self.cursor.execute("SELECT ProductName FROM Products WHERE ProductNo = ?", (product_no,))
            name = self.cursor.fetchone()[0]
            self.cursor.execute("DELETE FROM Products WHERE ProductNo = ?", (product_no,))
            self.connection.commit()
            self.logger.info(
                f"Delete Product | {product_no} - {name}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_inventory_table(self) -> list:
        """Returns: [InventoryID: int, ProductNo:str, Name: str, Description: str, Quantity, int, Location: str, BatchID: str]"""
        try:
            self.cursor.execute("""
            SELECT i.InventoryID, p.ProductNo, p.ProductName, p.Description, i.StockQuantity, l.LocationName, b.PBatchNumber
            FROM Inventory i LEFT JOIN Products p ON i.ProductID = p.ProductID
            LEFT JOIN Locations l ON i.LocationID = l.LocationID
            LEFT JOIN Product_Batch b ON i.PBatchID = b.PBatchID  
            """)
            results = [value for value in self.cursor.fetchall() if value[4] != 0]
            return results

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_inventory_updatable(self) -> dict:
        """Returns: {'ProductNo - ProductName' : 'Description' }"""
        try:
            self.cursor.execute("""
            SELECT DISTINCT p.ProductNo, p.ProductName, p.Description
            FROM Inventory i LEFT JOIN Products p ON i.ProductID = p.ProductID
            WHERE i.LocationID != 4
            """)
            inventory_dict = {f"{row[0]} - {row[1]}": row[2] for row in self.cursor.fetchall()}
            return inventory_dict

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return {}

    def query_inventory_location(self, productNo: str) -> list:
        """Returns: 'Location ID - Location Name (Quantity Remaining)'"""
        try:
            self.cursor.execute("""
            SELECT i.LocationID, l.LocationName, SUM(i.StockQuantity)
            FROM Inventory i INNER JOIN Locations l ON i.LocationID = l.LocationID
            INNER JOIN Products p ON i.ProductID = p.ProductID
            WHERE p.ProductNo = ? AND l.LocationName != ?
            GROUP BY i.LocationID
            """, (productNo, "Output"))
            values = self.cursor.fetchall()
            #print(values)
            return [f"{value[0]} - {value[1]} ({value[2]} Stock Remaining)" for value in values]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_inventory_productBatch(self, productNo: str, locationID: int) -> list:
        try:
            self.cursor.execute("""SELECT b.PBatchNumber, i.StockQuantity
            FROM Inventory i INNER JOIN Products p ON i.ProductID = p.ProductID 
            INNER JOIN Product_Batch b ON i.PBatchID = b.PBatchID 
            WHERE p.ProductNo = ? AND i.LocationID = ?
            """, (productNo, locationID,))
            return [f"{value[0]} ({value[1]} Stock Remaining)" for value in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_productBatchNo(self) -> list[str]:
        """Returns a list of all Product Batch Numbers in Inventory [PBatchNo - ProductName]"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT b.PBatchNumber ||' - ' || p.ProductName
                FROM Inventory i 
                INNER JOIN Product_Batch b ON i.PBatchID = b.PBatchID
                INNER JOIN Products p ON i.ProductID = p.ProductID
            """)
            return [row[0] for row in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_inventory_quantity(self, productNo: str, locationID: int, batchNo: str) -> int:
        try:
            self.cursor.execute(
                """SELECT i.StockQuantity 
                FROM Inventory i INNER JOIN Products p ON i.ProductID = p.ProductID
                INNER JOIN Product_Batch b ON i.PBatchID = b.PBatchID
                WHERE p.ProductNo = ? AND i.LocationID = ? AND b.PBatchNumber = ?""",
                (productNo, locationID, batchNo,))
            return self.cursor.fetchone()[0]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return 0

    def query_stock_quantity(self) -> int:
        """Returns total quantity of stock in inventory"""
        try:
            self.cursor.execute("""SELECT COALESCE(SUM(StockQuantity), 0) FROM Inventory WHERE LocationID != 5""")
            return self.cursor.fetchone()[0]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return 0

    def query_shipment_quantity(self) -> int:
        """Returns total quantity of stock in shipments"""
        try:
            self.cursor.execute("""SELECT COALESCE(SUM(Quantity), 0) FROM Shipments WHERE Status != 'Received'""")
            return self.cursor.fetchone()[0]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return 0

    def receive_inventory(self, shipmentNo: str, employee_id: int | None = None) -> bool:
                try:
                    self._require_role(employee_id, ("Worker", "Supervisor", "Administrator"))

                    self.cursor.execute("SELECT ProductID, Quantity, PBatchID FROM Shipments WHERE ShipmentNo = ?",
                                        (shipmentNo,))
                    productID, quantity, batchID = self.cursor.fetchone()

                    self.cursor.execute("""
                        INSERT INTO Inventory (ProductID, StockQuantity, LocationID, PBatchID)
                        VALUES (?, ?, ?, ?)
                    """, (productID, quantity, 1, batchID,))
                    self.cursor.execute("UPDATE Shipments SET Status = ? WHERE ShipmentNo = ?", ("Received", shipmentNo,))
                    self.connection.commit()

                    self.cursor.execute("SELECT ProductName FROM Products WHERE ProductID = ?", (productID,))
                    name = self.cursor.fetchone()[0]
                    self.cursor.execute("SELECT PBatchNumber FROM Product_Batch WHERE PBatchID = ?", (batchID,))
                    batchNumber = self.cursor.fetchone()[0]

                    if hasattr(self, 'logger'):
                        self.logger.info(f"{name} | {batchNumber} | Vendor | Input | {quantity}",
                                        type="report", key="Product Movement Report")
                    self._log_user_activity(employee_id, f"Receive Inventory | Shipment No: {shipmentNo}")
                    return True

                except PermissionError as e:
                    print(e)
                    return False
                except Exception as err:
                    print(f"Error: {err}")
                    return False

    def update_inventory(self, productNo: str, batchNumber: str, srcLocationID: int, desLocationID: int,
                         quantity: int, employee_id: int | None = None) -> bool:
        try:
            self._require_role(employee_id, ("Worker", "Supervisor", "Administrator"))

            self.cursor.execute("SELECT PBatchID FROM Product_Batch WHERE PBatchNumber = ?", (batchNumber,))
            batchID = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT ProductID FROM Products WHERE ProductNo = ?", (productNo,))
            productID = self.cursor.fetchone()[0]

            srcQuantity = self.cursor.execute("""
                SELECT StockQuantity FROM Inventory WHERE ProductID = ? AND PBatchID = ? AND LocationID = ?
            """, (productID, batchID, srcLocationID,))
            srcQuantity = int(srcQuantity.fetchone()[0]) - int(quantity)

            self.cursor.execute("""
                UPDATE Inventory 
                SET StockQuantity = ?
                WHERE ProductID = ? AND PBatchID = ? AND LocationID = ?
            """, (srcQuantity, productID, batchID, srcLocationID,))

            desQuantity = self.cursor.execute("""
                SELECT StockQuantity FROM Inventory WHERE ProductID = ? AND PBatchID = ? AND LocationID = ?
            """, (productID, batchID, desLocationID,))

            try:
                desQuantity = int(desQuantity.fetchone()[0]) + int(quantity)
                self.cursor.execute("""
                    UPDATE Inventory 
                    SET StockQuantity = ?
                    WHERE ProductID = ? AND PBatchID = ? AND LocationID = ?
                """, (desQuantity, productID, batchID, desLocationID,))
            except Exception:
                self.cursor.execute("""
                    INSERT INTO Inventory (ProductID, StockQuantity, LocationID, PBatchID)
                    VALUES (?, ?, ?, ?)
                """, (productID, quantity, desLocationID, batchID,))

            self.connection.commit()

            self.cursor.execute("""SELECT ProductName FROM Products WHERE ProductNo = ?""", (productNo,))
            name = self.cursor.fetchone()[0]
            self.cursor.execute("""SELECT LocationName FROM Locations WHERE LocationID = ? OR LocationID = ?""",
                                (srcLocationID, desLocationID,))
            locations = self.cursor.fetchall()

            if hasattr(self, 'logger'):
                self.logger.info(f"{name} | {batchNumber} | {locations[0][0]} | {locations[1][0]} | {quantity}",
                                 type="report", key="Product Movement Report")
            self._log_user_activity(
                employee_id,
                f"Update Inventory | Moved {quantity} units of {name} from {locations[0][0]} to {locations[1][0]}"
            )
            return True

        except PermissionError as e:
            print(e)
            return False
        except Exception as err:
            print(f"Error: {err}")
            return False

    def delete_inventory(self, inventoryID: int, employee_id: int | None = None) -> bool:
        try:
            self._require_role(employee_id, ("Supervisor", "Administrator"))

            self.cursor.execute("""SELECT p.ProductName, l.LocationName, COALESCE(i.StockQuantity, 0), b.PBatchNumber
                FROM Inventory i INNER JOIN Products p ON i.ProductID = p.ProductID
                INNER JOIN Locations l ON i.LocationID = l.LocationID
                INNER JOIN Product_Batch b ON i.PBatchID = b.PBatchID
                WHERE i.InventoryID = ?""", (inventoryID,))
            old_values = self.cursor.fetchone()

            self.cursor.execute("DELETE FROM Inventory WHERE InventoryID = ?", (inventoryID,))
            self.connection.commit()

            if old_values:
                self._log_user_activity(
                    employee_id,
                    f"Deleted Inventory | {old_values[2]} of {old_values[0]} at {old_values[1]} (Batch {old_values[3]})"
                )
            return True

        except PermissionError as e:
            print(e)
            return False
        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_vendor_all(self) -> list:
        """Returns: [(VendorNo: str, VendorName: str, Email: str, ContactNumber: str),]"""
        self.cursor.execute("SELECT * FROM Suppliers")
        return self.cursor.fetchall()

    def query_preferred_vendor(self, productID) -> str:
        try:
            self.cursor.execute("""SELECT s.SupplierID, s.Name FROM Suppliers s INNER JOIN Products p 
                            ON s.SupplierID = p.PreferredSupplierID WHERE p.ProductID = ?
                            """, (productID,))
            value = self.cursor.fetchone()
            return f"{value[0]} - {value[1]}"

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return ""

    def query_vendor(self) -> list:
        """Returns: [(VendorID: int, VendorName: str),]"""
        self.cursor.execute("SELECT SupplierID, Name FROM Suppliers")
        return self.cursor.fetchall()

    def add_vendor(self, name: str, email: str, contact_number: str) -> bool:
        try:
            self.cursor.execute("INSERT INTO Suppliers (Name, ContactNumber, Email) VALUES (?, ?, ?)",
                                (name, contact_number, email))
            self.connection.commit()
            self.logger.success("", event="New Vendor Created", type="notification")
            self.logger.info(f"Create Vendor | {name}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def update_vendor(self, supplier_id: int, name: str, contact_number: str, email: str) -> bool:
        try:
            self.cursor.execute("""SELECT Name, ContactNumber, Email FROM Suppliers WHERE SupplierID = ?""",
                                (supplier_id,))
            old_values = self.cursor.fetchone()

            self.cursor.execute("UPDATE Suppliers SET Name = ?, ContactNumber = ?, Email = ? WHERE SupplierID = ?",
                                (name, contact_number, email, supplier_id))
            self.connection.commit()

            for i, e in enumerate((("Name", name), ("Contact Number", contact_number), ("Email", email))):
                if str(old_values[i]) != e[1]:
                    self.logger.info(f"Update Vendor | {e[0]}: {old_values[i]} -> {e[1]}",
                                     type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def delete_vendor(self, supplier_id: int) -> bool:
        try:
            self.cursor.execute("SELECT Name FROM Suppliers WHERE SupplierID = ?", (supplier_id,))
            name = self.cursor.fetchone()[0]
            self.cursor.execute("DELETE FROM Suppliers WHERE SupplierID = ?", (supplier_id,))
            self.connection.commit()

            self.logger.info(f"Create Vendor | {name}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_task_table(self) -> list:
        self.cursor.execute("""
            SELECT TaskID, COALESCE(Task_Batch.TBatchNo, 'Not Assigned'), COALESCE(Workers.Name, 'Not Assigned'), 
            TaskDesc, TaskStatus, ETA
            FROM Tasks LEFT JOIN Task_Batch ON Tasks.TBatchID = Task_Batch.TBatchID
            LEFT JOIN Workers ON Tasks.WorkerID = Workers.WorkerID
        """)
        return self.cursor.fetchall()

    def query_task_updatable(self) -> list[str]:
        """Returns: [Task ID - Task Description, Assigned Employee, Progress, ETA] where Status is not 'Completed'"""
        self.cursor.execute('''SELECT TaskID || ' - ' || TaskDesc, COALESCE(Task_Batch.TBatchNo, 'Not Assigned'), 
                COALESCE(Workers.WorkerID || ' - ' || Workers.Name, 'Not Assigned'), TaskStatus,  ETA
                FROM Tasks LEFT JOIN Task_Batch ON Tasks.TBatchID = Task_Batch.TBatchID
                LEFT JOIN Workers ON Tasks.WorkerID = Workers.WorkerID
                WHERE TaskStatus != "Completed"''')
        return self.cursor.fetchall()

    def add_task(self, description: str, eta: str, worker_id: int, batch_id: int = None) -> bool:
        try:
            if re.match(r'\d+', str(worker_id)) is not None:
                self.cursor.execute("""
                    INSERT INTO Tasks (TaskDesc, WorkerID, ETA, TaskStatus, TBatchID)
                    VALUES (?, ?, ?, 'Not Started', ?)
                """, (description, worker_id, eta, batch_id))
            else:
                self.cursor.execute("""
                    INSERT INTO Tasks (TaskDesc, ETA, TaskStatus, TBatchID)
                    VALUES (?, ?, 'Not Started', ?)""", (description, eta, batch_id))
            self.connection.commit()
            self.logger.info(f"Create Task | {description}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def update_task(self, task_id: int, description: str, worker_id: int, progress: str, eta: str,
                    batch_no: str = None) -> bool:
        try:
            self.cursor.execute("""SELECT TBatchID FROM Task_Batch WHERE TBatchNo = ?""", (batch_no,))
            try:
                batch_id = self.cursor.fetchone()[0]
            except:
                batch_id = None
            if batch_id is not None:
                self.cursor.execute("""
                    UPDATE Tasks
                    SET TaskDesc = ?, WorkerID = ?, TaskStatus = ?, ETA = ?, TBatchID = ?
                    WHERE TaskID = ?
                """, (description, worker_id, progress, eta, batch_id, task_id,))
                self.logger.info(f"Update Task | Batch Assignment {batch_id}", type="report", key="User Activities")
            else:
                self.cursor.execute("""SELECT TaskDesc, WorkerID, TaskStatus, ETA FROM Tasks WHERE TaskID = ?""",
                                    (task_id,))
                old_values = [value for value in self.cursor.fetchone()]
                self.cursor.execute("SELECT Name FROM Workers WHERE WorkerID = ?", (old_values[1],))
                old_values[1] = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT Name FROM Workers WHERE WorkerID = ?", (worker_id,))
                new_worker_name = self.cursor.fetchone()[0]

                self.cursor.execute("""
                    UPDATE Tasks
                    SET TaskDesc = ?, WorkerID = ?, TaskStatus = ?, ETA = ?, TBatchID = NULL
                    WHERE TaskID = ?
                """, (description, worker_id, progress, eta, task_id,))

                for i, e in enumerate(
                        (("Task Description", description), ("Worker", new_worker_name), ("Task Status", progress),
                         ("ETA", eta))):
                    if old_values[i] != e[1]:
                        self.logger.info(f"Update Task | {e[0]}: {old_values[i]} -> {e[1]}", type="report",
                                         key="User Activities")
            self.connection.commit()
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def delete_task(self, task_id: int) -> bool:
        try:
            self.cursor.execute("SELECT TaskDesc FROM Tasks WHERE TaskID = ?", (task_id,))
            desc = self.cursor.fetchone()[0]
            self.cursor.execute("DELETE FROM Tasks WHERE TaskID = ?", (task_id,))
            self.connection.commit()
            self.logger.info(f"Delete Task | {desc}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_taskBatch(self) -> list[str]:
        """Returns: [Task Batch - Task Description]"""
        try:
            self.cursor.execute("SELECT TBatchNo || ' - ' || TBatchDesc FROM Task_Batch")
            return [value[0] for value in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def add_taskBatch(self, batchDesc: str, batchNo: str, taskIDs: list) -> bool:
        try:
            self.cursor.execute("INSERT INTO Task_Batch (TBatchNo, TBatchDesc) VALUES (?, ?)", (batchNo, batchDesc,))
            self.cursor.execute("SELECT TBatchID FROM Task_Batch WHERE TBatchDesc = ?", (batchDesc,))
            batchID = self.cursor.fetchone()[0]
            for i in taskIDs:
                self.cursor.execute("""
                    UPDATE Tasks
                    SET TBatchID = ?
                    WHERE TaskID = ?
                """, (batchID, i,))
            self.connection.commit()
            return True
        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def update_taskBatch(self, batchNo: str, batchDesc: str = "", taskIDs: list = [], employeeID: int = 0) -> bool:
        try:
            self.cursor.execute("""SELECT TBatchID FROM Task_Batch WHERE TBatchNo = ?""", (batchNo,))
            batchID = self.cursor.fetchone()[0]

            self.cursor.execute("UPDATE Task_Batch SET TBatchDesc = ? WHERE TBatchID = ?", (batchDesc, batchID,))

            if taskIDs:
                self.cursor.execute("UPDATE Tasks SET TBatchID = NULL WHERE TBatchID = ?", (batchID,))
                for index in taskIDs:
                    self.cursor.execute("UPDATE Tasks SET TBatchID = ? WHERE TaskID = ?", (batchID, index))

            if employeeID != 0:
                self.cursor.execute("UPDATE Tasks SET WorkerID = ? WHERE TBatchID =?", (employeeID, batchID))

            self.connection.commit()
            return True

        except TypeError:
            print("type error, python's best friend")
            return False

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def delete_taskBatch(self, batchID: int) -> bool:
        try:
            self.cursor.execute("""UPDATE Tasks SET TBatchID = NULL WHERE TBatchID = ?""", (batchID,))
            self.cursor.execute("""DELETE FROM Task_Batch WHERE TBatchID = ?""", (batchID,))
            self.connection.commit()
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_purchaseOrder_dashboard(self) -> list[int]:
        """Returns parameters for the dashboard purchase activity frame widget."""
        try:
            results = []
            self.cursor.execute("""SELECT COALESCE(COUNT(ShipmentID), 0) FROM Shipments""")
            results.append(self.cursor.fetchone()[0])
            self.cursor.execute("""SELECT COALESCE(COUNT(ShipmentID), 0) FROM Shipments WHERE Status = 'In Transit'""")
            results.append(self.cursor.fetchone()[0])
            self.cursor.execute("""SELECT COALESCE(COUNT(ShipmentID), 0) FROM Shipments WHERE Status = 'Received'""")
            results.append(self.cursor.fetchone()[0])
            self.cursor.execute("""SELECT COALESCE(SUM(Quantity), 0) FROM Shipments WHERE Status = 'Received'""")
            results.append(self.cursor.fetchone()[0])
            return [int(value) for value in results]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return [0, 0, 0, 0]

    def query_purchaseOrder_receivables(self) -> list:
        """Returns: [ShipmentNo, ProductNo, ProductName, ProductDesc, Quantity, VendorId - VendorName]"""
        try:
            self.cursor.execute("""SELECT s.ShipmentNo, p.ProductNo, p.ProductName, p.Description, s.Quantity, v.SupplierID, v.Name
                FROM Shipments s LEFT JOIN Products p ON s.ProductID = p.ProductID
                LEFT JOIN Suppliers v ON s.SupplierID = v.SupplierID
                WHERE s.Status != ?""", ("Received",))
            returnList = [list(value) for value in self.cursor.fetchall()]
            for element in returnList:
                element[-2] = f"{element[-2]} - {element[-1]}"
                element.pop()
            return returnList

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_purchaseOrder(self):
        """Returns: [Purchase No: str, Product Name: str, Quantity: int, Batch Number: str, Vendor Name: str, Date: str, Status: str]"""
        try:
            self.cursor.execute("""
                SELECT s.ShipmentNo, p.ProductName, s.Quantity, b.PBatchNumber, v.Name, s.ShipmentDate, s.Status
                FROM Shipments s 
                LEFT JOIN Products p ON s.ProductID = p.ProductID
                LEFT JOIN Suppliers v ON s.SupplierID = v.SupplierID
                LEFT JOIN Product_Batch b ON s.PBatchID = b.PBatchID
            """)
            return self.cursor.fetchall()

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def add_purchaseOrder(self, productID: int, quantity: int, vendorID: int, batchNo: str) -> bool:
        try:
            try:
                self.cursor.execute("SELECT ShipmentNo FROM Shipments ORDER BY ShipmentID Desc LIMIT 1")
                shipmentID = self._generateID(self.cursor.fetchone()[0])
            except:
                shipmentID = self._generateID("SHIP-000000-A")
            if re.match("^BATCH-[\d]{6}-[A-Z]+$", batchNo):
                self.cursor.execute("SELECT PBatchNumber FROM Product_Batch")
                if batchNo not in [value[0] for value in self.cursor.fetchall()]:
                    self.cursor.execute("INSERT INTO Product_Batch (PBatchNumber) VALUES (?)", (batchNo,))
                    batchID = self.cursor.lastrowid
                else:
                    self.cursor.execute("SELECT PBatchID FROM Product_Batch WHERE PBatchNumber = ?", (batchNo,))
                    batchID = self.cursor.fetchone()[0]
                self.cursor.execute("""INSERT INTO Shipments (ShipmentNo, ProductID, Quantity, SupplierID, ShipmentDate, PBatchID)
                                VALUES (?, ?, ?, ?, ?, ?)""",
                                    (shipmentID, productID, quantity, vendorID, date.today(), batchID,))
                self.connection.commit()

                self.logger.success("", event="New Purchase Order Created", type="notification")
                self.logger.info(f"Add Purchase Order | {shipmentID}", type="report", key="User Activities")
                return True
            else:
                return False

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def update_purchaseOrder(self, shipmentNo: str, productID: int, quantity: int, vendorID: int, Status: str) -> bool:
        try:
            self.cursor.execute("""SELECT p.ProductName, s.Quantity, v.Name, s.Status
                FROM Shipments s LEFT JOIN Products p ON s.ProductID = p.ProductID
                LEFT JOIN Suppliers v ON s.SupplierID = v.SupplierID
                WHERE s.ShipmentNo = ?""", (shipmentNo,))
            old_values = self.cursor.fetchone()

            self.cursor.execute("""
                UPDATE Shipments SET ProductID = ?, Quantity = ?, SupplierID = ?, Status = ?
                WHERE ShipmentNo = ?
            """, (productID, quantity, vendorID, Status, shipmentNo))
            self.connection.commit()

            self.cursor.execute("""SELECT ProductName FROM Products WHERE ProductID = ?""", (productID,))
            name = self.cursor.fetchone()[0]
            self.cursor.execute("""SELECT Name FROM Suppliers WHERE SupplierID = ?""", (vendorID,))
            vendor_name = self.cursor.fetchone()[0]

            for i, e in enumerate(
                    (("Product Name", name), ("Quantity", quantity), ("Vendor", vendor_name), ("Status", Status))):
                if str(old_values[i]) != e[1]:
                    self.logger.info(f"Update Purchase Order | {shipmentNo} {e[0]}: {old_values[i]} -> {e[1]}",
                                     type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def delete_purchaseOrder(self, purchaseOrderNo: str) -> bool:
        try:
            self.cursor.execute("DELETE FROM Shipments WHERE ShipmentNo = ?", (purchaseOrderNo,))
            self.logger.info(f"Delete Purchase Order | {purchaseOrderNo}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def query_stock_sold(self) -> int:
        """Returns quantity of stock sold"""
        try:
            self.cursor.execute("""SELECT COALESCE(SUM(i.QuantitySold), 0)
                FROM Sales_Inventory i INNER JOIN Sales s ON i.SaleID=s.SaleID
                WHERE Status = 'Delivered'""")
            return self.cursor.fetchone()[0]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return 0

    def query_SalesOrder(self) -> list:
        """Returns all SaleNo IDs"""
        try:
            self.cursor.execute("SELECT SaleNo FROM Sales")
            return [value for value in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_newSalesOrder(self) -> list:
        """Returns all unvalidated SaleNo IDs"""
        try:
            self.cursor.execute("SELECT SaleNo FROM Sales WHERE Status = 'Not Paid'")
            return [value[0] for value in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_updatableSalesOrder(self) -> list:
        """Returns all undelivered SaleNo IDs"""
        try:
            self.cursor.execute("SELECT SaleNo FROM Sales WHERE Status = 'Not Delivered'")
            return [value[0] for value in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_salesOrder_delivered(self) -> list:
        """Returns all delivered SaleNo IDs"""
        try:
            self.cursor.execute("SELECT SaleNo FROM Sales WHERE Status = 'Delivered'")
            return [value[0] for value in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_salesOrder_validatable(self) -> list[str]:
        """Returns: [SaleNo, Date, Total Price, Status]"""
        try:
            self.cursor.execute(""" 
                SELECT s.SaleNo, s.Date, SUM(i.QuantitySold * p.Price), s.Status
                FROM Sales s INNER JOIN Sales_Inventory i ON s.SaleID = i.SaleID 
                INNER JOIN Products p ON i.ProductID = p.ProductID
                GROUP BY s.SaleNo
            """)
            return self.cursor.fetchall()

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_salesOrder_table(self) -> list:
        """Returns nested list: ["SaleNo", "ProductSold", "Quantity", "BatchNo", "Date", "Status"]"""
        try:
            self.cursor.execute("""
                SELECT s.SaleNo, p.ProductNo || ' ' || p.ProductName, i.QuantitySold || ' (' || COALESCE(SUM(b.QuantityTaken), 0) || ' Assigned)', COALESCE(GROUP_CONCAT(pb.PBatchNumber), 'Not Assigned'), s.Date, s.Status
                FROM Sales s INNER JOIN Sales_Inventory i ON s.SaleID = i.SaleID
                LEFT JOIN Products p ON i.ProductID = p.ProductID
                LEFT JOIN Sales_Inventory_Batch b ON i.SalesInventoryID = b.SalesInventoryID
                LEFT JOIN Product_Batch pb ON b.PBatchID = pb.PBatchID
                GROUP BY i.SalesInventoryID
            """)
            return self.cursor.fetchall()

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_saleDetails_table(self, saleNo: str) -> list[list[str]]:
        """Returns: [Product Name, Batch No, Unit Price, Quantity, Total Price]"""
        try:
            self.cursor.execute("""
                SELECT p.ProductNo || ' ' || p.ProductName, COALESCE(GROUP_CONCAT(pb.PBatchNumber), 'Not Assigned'), p.Price, i.QuantitySold || ' (' || COALESCE(SUM(sb.QuantityTaken), 0) || ' Assigned)', (p.Price * i.QuantitySold)
                FROM Sales_Inventory i INNER JOIN Sales s ON i.SaleID = s.SaleID
                INNER JOIN Products p ON i.ProductID = p.ProductID
                LEFT JOIN Sales_Inventory_Batch sb ON i.SalesInventoryID = sb.SalesInventoryID
                LEFT JOIN Product_Batch pb ON sb.PBatchID = pb.PBatchID
                WHERE s.SaleNo = ?
                GROUP BY p.ProductID
            """, (saleNo,))
            result = [list(value) for value in self.cursor.fetchall()]
            for value in result:
                value[-1] = f"{round(value[-1], 2):,}"
            return result

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_salesorder_product(self, saleNo: str) -> list[str]:
        """
        Returns products to be sold and quantity to be delivered for a Sale No.
        [Product No] - [Product Name] ([Quantity Sold in SaleNo. - QuantityTaken for SaleNo] units to be delivered)
        """
        try:
            self.cursor.execute("""
                SELECT COALESCE(p.ProductNo || ' - ' || p.ProductName || ' (' || (i.QuantitySold - IFNULL(SUM(b.QuantityTaken), 0)) || ' units to be delivered)', 'No Products Assigned')
                FROM Sales_Inventory i RIGHT JOIN Sales s ON i.SaleID = s.SaleID
                LEFT JOIN Products p ON i.ProductID = p.ProductID
                LEFT JOIN Sales_Inventory_Batch b ON i.SalesInventoryID = b.SalesInventoryID
                WHERE s.SaleNo = ?
                GROUP BY p.ProductID
                ORDER BY p.ProductID ASC
            """, (saleNo,))
            return [value[0] for value in self.cursor.fetchall()]

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return 0

    def query_salesOrder_productBatch(self, productNo: str) -> list[str]:
        """Returns [Product Batch No.] ([Units Left]) that has not been assigned in the warehouse."""
        try:
            self.cursor.execute("""SELECT pb.PBatchNumber, SUM(i.StockQuantity)
                FROM Inventory i INNER JOIN Products p ON i.ProductID = p.ProductID
                INNER JOIN Product_Batch pb ON i.PBatchID = pb.PBatchID
                WHERE p.ProductNo = ? AND i.LocationID != 5
                GROUP BY pb.PBatchNumber
            """, (productNo,))
            results = [list(value) for value in self.cursor.fetchall()]
            for value in results:
                self.cursor.execute("""SELECT SUM(i.QuantityTaken) 
                    FROM Sales_Inventory_Batch i INNER JOIN Sales_Inventory s ON i.SalesInventoryID = s.SalesInventoryID
                    LEFT JOIN Product_Batch b ON i.PBatchID = b.PBatchID
                    WHERE PBatchNumber = ? GROUP BY s.ProductID""", (value[0],))
                try:
                    qty = self.cursor.fetchone()[0]
                    value[1] = int(value[1]) - int(qty)
                except TypeError as Err:
                    print(f"Type Error aaaAaaaAaaa\n{Err}")
            results = [f"{value[0]} ({value[1]} units left in warehouse)" for value in results]
            return results

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return []

    def query_salesOrder_quantity(self, productID: int) -> int:
        """Returns products available to be sold in the warehouse, and products at output."""
        try:
            self.cursor.execute(
                """SELECT SUM(StockQuantity) FROM Inventory WHERE ProductID = ? AND LocationID != 5 GROUP BY ProductID """,
                (productID,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as err:
            print(f"Error: {err}")
            return 0

    def create_salesOrder(self) -> bool:
        try:
            try:
                self.cursor.execute("SELECT SaleNo FROM Sales ORDER BY SaleID Desc LIMIT 1")
                saleNo = self._generateID(self.cursor.fetchone()[0])
            except:
                saleNo = self._generateID("SALE-000000-A")
            self.cursor.execute("INSERT INTO Sales (SaleNo, Date) VALUES (?, ?)", (saleNo, date.today(),))
            self.connection.commit()
            self.logger.success("", event="New Sales Order Created", type="notification")
            self.logger.info(f"Create Sales Order | {saleNo}", type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def add_salesOrder(self, saleNo: str, productID: str, quantity: int) -> bool:
        """
        1. Check if there's a salesInventory
        2a. If no, create a new row for it
        2b. If yes, update it to the new quantity
        """
        try:
            self.cursor.execute("SELECT SaleID FROM Sales WHERE SaleNO = ?", (saleNo,))
            saleID = self.cursor.fetchone()[0]
            self.cursor.execute("""SELECT SalesInventoryID FROM Sales_Inventory WHERE SaleID = ? AND ProductID = ?""",
                                (saleID, productID,))
            if self.cursor.fetchone() is None:
                self.cursor.execute("INSERT INTO Sales_Inventory (SaleID, ProductID, QuantitySold) VALUES ( ?, ?, ?)",
                                    (saleID, productID, quantity,))
            else:
                self.cursor.execute(
                    """UPDATE Sales_Inventory SET QuantitySold = QuantitySold + ? WHERE SaleID = ? AND ProductID = ?""",
                    (quantity, saleID, productID,))
            self.connection.commit()

            self.cursor.execute("""SELECT ProductName FROM Products WHERE ProductID = ?""", (productID,))
            name = self.cursor.fetchone()[0]
            self.logger.info(f"Add Sales Order | Add {quantity} {name} to {saleNo}", type="report",
                             key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def update_salesOrder(self, saleNo: str, productNo: str, batchNo: str, quantity: int) -> bool:
        try:
            self.cursor.execute("""SELECT i.SalesInventoryID 
                FROM Sales_Inventory i INNER JOIN Products p ON i.ProductID = p.ProductID
                INNER JOIN Sales s ON i.SaleID = s.SaleID
                WHERE s.SaleNo = ? AND p.ProductNo = ?
            """, (saleNo, productNo))
            salesInventoryID = self.cursor.fetchone()[0]

            self.cursor.execute("""SELECT PBatchID FROM Product_Batch WHERE PBatchNumber = ?""", (batchNo,))
            batchID = self.cursor.fetchone()[0]

            self.cursor.execute("""SELECT ProductName FROM Products WHERE ProductNo = ?""", (productNo,))
            name = self.cursor.fetchone()[0]

            self.cursor.execute("""SELECT SalesInventoryBatchID FROM Sales_Inventory_Batch
                WHERE SalesInventoryID = ? AND PBatchID = ?""", (salesInventoryID, batchID))
            try:
                _ = self.cursor.fetchone()[0]
                self.cursor.execute("""UPDATE Sales_Inventory_Batch SET QuantityTaken = (QuantityTaken+?)""",
                                    (quantity,))
            except:
                self.cursor.execute("""INSERT INTO Sales_Inventory_Batch (SalesInventoryID, PBatchID, QuantityTaken)
                    VALUES (?, ?, ?)""", (salesInventoryID, batchID, quantity,))
            self.connection.commit()
            self.logger.info(f"Update Sales Order | Assigned {quantity} {name} from {batchNo} to {saleNo}",
                             type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def validate_salesOrder(self, saleDetails: str) -> bool:
        try:
            if saleDetails.split('(')[1] == "Not Paid)":
                newStatus = "Not Delivered"
            else:
                newStatus = "Delivered"
                self.cursor.execute(
                    """SELECT i.PBatchID FROM Sales_Inventory i INNER JOIN Sales s ON i.SaleID=s.SaleID WHERE s.SaleNo = ?""",
                    (saleDetails.split(' (')[0],))
                for value in self.cursor.fetchall():
                    if value[0] is None:
                        return False
            self.cursor.execute("UPDATE Sales SET STATUS = ? WHERE SaleNo = ?",
                                (newStatus, saleDetails.split(' (')[0],))
            self.connection.commit()
            self.logger.info(f"Validate Sales Order | Validated Payment for {saleDetails.split(' (')[0]}",
                             type="report", key="User Activities")
            return True

        except Exception as err:
            print(f"Error: {err}")
            return False

    def update_salesOrder_delivery(self, saleNo: str) -> bool:
        if not self.validate_salesOrder_delivery(saleNo):
            return False
        try:
            self.cursor.execute("""SELECT i.ProductID, b.QuantityTaken, b.PBatchID
                FROM Sales_Inventory_Batch b INNER JOIN Sales_Inventory i ON b.SalesInventoryID = i.SalesInventoryID
                INNER JOIN Sales s ON i.SaleID = s.SaleID
                WHERE SaleNo = ?
            """, (saleNo,))
            results = self.cursor.fetchall()

            for result in results:
                self.cursor.execute("""SELECT StockQuantity FROM Inventory
                    WHERE ProductID = ? AND LocationID = 4 AND PBatchID = ? """, (result[0], result[2],))
                qty = self.cursor.fetchone()[0] - result[1]
                self.cursor.execute("""UPDATE Inventory SET StockQuantity = ?
                    WHERE ProductID = ? AND LocationID = 4 AND PBatchID = ?
                """, (qty, result[0], result[2],))

                self.cursor.execute(
                    """SELECT InventoryID FROM Inventory WHERE ProductID = ? AND LocationID = 5 AND PBatchID = ?""",
                    (result[0], result[2]))
                if self.cursor.fetchone() is None:
                    self.cursor.execute("""INSERT INTO Inventory (ProductID, StockQuantity, LocationID, PBatchID)
                        VALUES (?, ?, 5, ?) """, (result[0], result[1], result[2]))
                else:
                    self.cursor.execute("""UPDATE Inventory SET StockQuantity = StockQuantity + ?
                        WHERE ProductID = ? AND LocationID = 5 AND PBatchID = ?
                    """, (result[1], result[0], result[2],))

            self.cursor.execute("""UPDATE Sales SET Status = 'Delivered' WHERE SaleNo = ?""", (saleNo,))
            self.connection.commit()

            for result in results:
                self.cursor.execute("""SELECT COALESCE(SUM(i.StockQuantity), 0), p.ProductName
                    FROM Inventory i INNER JOIN Products p ON i.ProductID = p.ProductID
                    WHERE i.LocationID!=5 AND i.ProductID = ?""", (result[0],))
                product = self.cursor.fetchone()
                qty_left, prod_name = int(product[0]), product[1]
                if qty_left == 0:
                    self.logger.success("", event="Out of Stock Alert", placeholder=prod_name, type="notification")
                elif qty_left <= 20:
                    self.logger.success("", event="Stock at Critical Level", placeholder=prod_name, type="notification")
                elif qty_left <= 40:
                    self.logger.success("", event="Low Stock Alert", placeholder=prod_name, type="notification")

                self.cursor.execute("SELECT PBatchNumber FROM Product_Batch WHERE PBatchID = ?", (result[2],))
                batchNumber = self.cursor.fetchone()[0]
                self.logger.info(f"{product[1]} | {batchNumber} | Output | Customer | {result[1]}",
                                 type="report", key="Product Movement Report")

            self.logger.info(f"Validate Sales Order | Validated Delivery for {saleNo}",
                             type="report", key="User Activities")
            return True

        except sqlite3.Error as err:
            print(f"Delivery Update Error: {err}")
            return False

    def validate_salesOrder_delivery(self, saleNo: str) -> bool:
        try:
            self.cursor.execute("""SELECT i.ProductID, b.PBatchID, COALESCE(b.QuantityTaken, 0)
                FROM Sales_Inventory i INNER JOIN Sales s ON i.SaleID = s.SaleID
                LEFT JOIN Sales_Inventory_Batch b ON i.SalesInventoryID = b.SalesInventoryID
                WHERE s.SaleNo = ?
            """, (saleNo,))
            results = [list(value) for value in self.cursor.fetchall()]
            for result in results:
                self.cursor.execute(
                    """SELECT StockQuantity FROM Inventory WHERE ProductID = ? AND LocationID = 4 AND PBatchID = ?""",
                    (result[0], result[1],))
                try:
                    result += [self.cursor.fetchone()[0]]
                except TypeError:
                    result += [0]
            for result in results:
                if result[2] > result[3]:
                    return False
            self.cursor.execute("""SELECT i.QuantitySold, COALESCE(SUM(b.QuantityTaken), 0)
                FROM Sales_Inventory i INNER JOIN Sales s ON i.SaleID = s.SaleID
                INNER JOIN Sales_Inventory_Batch b ON i.SalesInventoryID = b.SalesInventoryID
                WHERE s.SaleNo = ? GROUP BY i.SalesInventoryID""", (saleNo,))
            for value in self.cursor.fetchall():
                if value[0] > value[1]:
                    return False
            self.connection.commit()
            return True
        except sqlite3.Error as err:
            print(f"Delivery Validation Error: {err}")
            return False

    def delete_salesOrder(self, saleNo: str) -> bool:
        try:
            self.cursor.execute(
                "DELETE FROM Sales_Inventory WHERE SaleID IN (SELECT SaleID FROM Sales WHERE SaleNo = ?)", (saleNo,))
            self.cursor.execute("DELETE FROM Sales WHERE SaleNo = ?", (saleNo,))
            self.connection.commit()
            try:
                self._log_user_activity(getattr(self, 'employeeID', None), f"Delete Sales Order | {saleNo}")
            except Exception:
                pass
            return True

        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def deleteAccount(self, employeeID: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM Accounts WHERE WorkerID = ?", (employeeID,))
            self.cursor.execute("UPDATE Tasks SET WorkerID = NULL WHERE WorkerID = ?", (employeeID,))
            self.cursor.execute("DELETE FROM Workers WHERE WorkerID = ?", (employeeID,))
            self.connection.commit()
            return True
        except sqlite3.Error as err:
            print(f"Error: {err}")
            return False

    def _generateID(self, latestID: str) -> str:
        try:
            string = latestID.split('-')
            if string[1] != date.today().strftime('%y%m%d'):
                return f"{string[0]}-{date.today().strftime('%y%m%d')}-A"
            else:
                return f"{string[0]}-{string[1]}-{self.__increment_alphabet__(string[2])}"
        except:
            return ""

    def __increment_alphabet__(self, string: str) -> str:
        """Increments alphabets, e.g. A->B, Z->AA, ABZ-> ACA"""
        overflow = 1
        newString = ""
        for char in string[::-1]:
            asciiNum = ord(char) + overflow
            overflow = 0
            if asciiNum > 90:
                asciiNum -= 26
                overflow = 1
            newString += chr(asciiNum)
        return newString[::-1]

    def _create_tables(self):
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Roles (
            RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoleName TEXT(64) NOT NULL);
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Workers (
            WorkerID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoleID INTEGER NOT NULL,
            Name TEXT NOT NULL,
            ContactNumber TEXT(12),
            FOREIGN KEY (RoleID) REFERENCES Roles(RoleID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Accounts (
            WorkerID INTEGER PRIMARY KEY,
            Email TEXT UNIQUE NOT NULL,
            HashedPW TEXT(72) NOT NULL,
            FOREIGN KEY (WorkerID) REFERENCES Workers(WorkerID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Task_Batch (
            TBatchID INTEGER PRIMARY KEY AUTOINCREMENT,
            TBatchNo TEXT UNIQUE,
            TBatchDesc TEXT);
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tasks (
            TaskID INTEGER PRIMARY KEY AUTOINCREMENT,
            WorkerID INTEGER,
            TaskDesc TEXT,
            TaskStatus TEXT,
            ETA TEXT,
            TBatchID INTEGER,
            FOREIGN KEY (TBatchID) REFERENCES Task_Batch(TBatchID),
            FOREIGN KEY (WorkerID) REFERENCES Workers(WorkerID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notification (
            NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoleID INTEGER NOT NULL,
            TimeStamp TEXT,
            NotificationDesc TEXT,
            FOREIGN KEY (RoleID) REFERENCES Roles(RoleID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Product_Batch (
            PBatchID INTEGER PRIMARY KEY AUTOINCREMENT,
            PBatchNumber TEXT);
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Email TEXT,
            ContactNumber INTEGER(12));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Locations (
            LocationID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationName TEXT(64) NOT NULL);
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductNo TEXT UNIQUE NOT NULL,
            ProductName TEXT NOT NULL,
            Description TEXT,
            Price REAL,
            PreferredSupplierID INTEGER NOT NULL,
            FOREIGN KEY (PreferredSupplierID) REFERENCES Suppliers(SupplierID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Inventory (
            InventoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProductID INTEGER NOT NULL,
            StockQuantity INTEGER,
            LocationID INTEGER,
            PBatchID INTEGER,
            FOREIGN KEY (PBatchID) REFERENCES Product_Batch(PBatchID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
            FOREIGN KEY (LocationID) REFERENCES Locations(LocationID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Shipments (
            ShipmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            ShipmentNo TEXT UNIQUE NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL,
            SupplierID INTEGER NOT NULL,
            ShipmentDate TEXT NOT NULL,
            PBatchID TEXT NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Not Received',
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
            FOREIGN KEY (PBatchID) REFERENCES Product_Batch(PBatchID),
            FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID));
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales (
            SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleNo TEXT UNIQUE NOT NULL,
            Date TEXT,
            Status TEXT NOT NULL DEFAULT 'Not Paid');
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales_Inventory (
            SalesInventoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            QuantitySold INTEGER,
            FOREIGN KEY (SaleID) REFERENCES Sales(SaleID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID));
        ''')

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sales_Inventory_Batch (
            SalesInventoryBatchID INTEGER PRIMARY KEY AUTOINCREMENT,
            SalesInventoryID INTEGER NOT NULL,
            PBatchID TEXT NOT NULL,
            QuantityTaken INTEGER DEFAULT 0,
            FOREIGN KEY (SalesInventoryID) REFERENCES Sales_Inventory(SalesInventoryID),
            FOREIGN KEY (PBatchID) REFERENCES Product_Batch(PBatchID));
        """)

        self.cursor.execute("INSERT INTO Roles (RoleName) VALUES ('Administrator');")
        self.cursor.execute("INSERT INTO Roles (RoleName) VALUES ('Supervisor');")
        self.cursor.execute("INSERT INTO Roles (RoleName) VALUES ('Worker');")

        self.cursor.execute("INSERT INTO Locations (LocationName) VALUES ('Input');")
        self.cursor.execute("INSERT INTO Locations (LocationName) VALUES ('Warehouse');")
        self.cursor.execute("INSERT INTO Locations (LocationName) VALUES ('Packing Zone');")
        self.cursor.execute("INSERT INTO Locations (LocationName) VALUES ('Output');")
        self.cursor.execute("INSERT INTO Locations (LocationName) VALUES ('Customer');")

        self.cursor.execute("INSERT INTO Workers (RoleID, Name, ContactNumber) VALUES (1, 'Ahmad', '0161123344');")
        self.cursor.execute("INSERT INTO Accounts (WorkerID, Email, HashedPW) VALUES (1, 'ahmad@gmail.com', ?)",
                            (b'$2b$14$OQM2OwY9kdaOeA/IE0hhPeXwrQhbZwVxxJvlynbkRDfXB1dm6XSOy',))
<<<<<<< HEAD
=======
        
            # =======================
    # ===== OTP support =====
    # =======================

    def _ensure_otp_table(self):
        cur = self.connection.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS OTP_Codes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          WorkerID INTEGER NOT NULL,
          CodeHash TEXT NOT NULL,
          CreatedAt INTEGER NOT NULL,
          ExpiresAt INTEGER NOT NULL,
          ConsumedAt INTEGER,
          Attempts INTEGER NOT NULL DEFAULT 0
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_otp_worker ON OTP_Codes(WorkerID);")
        self.connection.commit()
        cur.close()

    def otp_insert(self, worker_id: int, code_hash: bytes, ttl_sec: int):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO OTP_Codes(WorkerID, CodeHash, CreatedAt, ExpiresAt) VALUES (?, ?, ?, ?)",
            (worker_id, code_hash.decode() if isinstance(code_hash, bytes) else code_hash, now(), now()+ttl_sec)
        )
        self.connection.commit()
        cur.close()

    def otp_get_latest_active(self, worker_id: int):
        cur = self.connection.cursor()
        cur.execute(
            """SELECT id, CodeHash, ExpiresAt, Attempts
               FROM OTP_Codes
               WHERE WorkerID=? AND ConsumedAt IS NULL
               ORDER BY id DESC LIMIT 1""",
            (worker_id,)
        )
        row = cur.fetchone()
        cur.close()
        return row

    def otp_consume(self, otp_id: int):
        cur = self.connection.cursor()
        cur.execute("UPDATE OTP_Codes SET ConsumedAt=? WHERE id=?", (now(), otp_id))
        self.connection.commit()
        cur.close()

    def otp_inc_attempt(self, otp_id: int):
        cur = self.connection.cursor()
        cur.execute("UPDATE OTP_Codes SET Attempts=Attempts+1 WHERE id=?", (otp_id,))
        self.connection.commit()
        cur.close()

    def otp_cleanup(self):
        cur = self.connection.cursor()
        cur.execute("DELETE FROM OTP_Codes WHERE (ConsumedAt IS NOT NULL) OR (ExpiresAt < ?)", (now(),))
        self.connection.commit()
        cur.close()

    # --- Logs helpers ---
    def log_event(self, actor_id: int, actor_name: str, action: str,
                  target_type: str, target_id: str|int|None, detail: str=""):
        cur = self.connection.cursor()
        cur.execute(
            "INSERT INTO Logs(actor_id, actor_name, action, target_type, target_id, detail) "
            "VALUES(?, ?, ?, ?, ?, ?)",
            (actor_id, actor_name, action, target_type, str(target_id) if target_id is not None else None, detail)
        )
        self.connection.commit()
        cur.close()

    def logs_latest(self, limit: int = 50):
        cur = self.connection.cursor()
        cur.execute("""
            SELECT id, actor_name, action, target_type, target_id,
                   datetime(created_at, 'unixepoch') as ts
            FROM Logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows

    def logs_by_actor(self, actor_id: int, limit: int = 50):
        cur = self.connection.cursor()
        cur.execute("""
            SELECT id, actor_name, action, target_type, target_id,
                   datetime(created_at, 'unixepoch') as ts
            FROM Logs
            WHERE actor_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (actor_id, limit))
        rows = cur.fetchall()
        cur.close()
        return rows
    
    def logs_latest(self, limit: int = 100):
        cur = self.conn.cursor() if hasattr(self, "conn") else self.connection.cursor()
        cur.execute("""
            SELECT id, actor_name, action, target_type, target_id,
                    datetime(created_at, 'unixepoch') as ts
            FROM Logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows  # [(_id, actor_name, action, target_type, target_id, ts), ...]




# Test Case
if __name__ == "__main__":
    #print(datetime.now())
    #auth = authentication()
    #if auth.authenticate("ahmad@gmail.com", "admin1234"):
    #    print("true")

    #if auth.authenticate("john@example.com", "JohnIsDumb"):
    #    print ("true")

    """
    auth.createAccount(
        adminID=1,
        adminPassword="admin1234",
        employeeEmail="john@example.com",
        employeeName="John Doe",
        employeeRoleID=2,
        employeeContactNumber="123-456-7890",
        employeePassword="JohnIsDumb"
    )
    """
    #auth.createAccount(

    #)

    con = DatabaseConnection()
    #con.add_productBatch("BATCH-240602-ABZ")
    #print(con.query_productBatchNo())
    #con.update_product('FUR-TBL-M-BR-001', 'Wooden Dining Table', 'Sturdy table for 6 people', 289.99, 1)
    #print(con.update_salesOrder('SALE-240610-A', 'FUR-CHR-M-BR-001', 'BATCH-240526-A', 7))
    #print(con.query_salesOrder_productBatch('FUR-CHR-M-BR-001'))
    #con.validate_salesOrder_delivery('SALE-240612-A')
    #con.update_salesOrder_delivery('SALE-240612-A')
    #print(con.query_taskBatch())
    #con.update_task(3, 'Review code for pull request', 2, 'In Progress', '2024-05-27', 'TASK-240611-A')
    #print(con.query_accounts_table())
    #print(con.query_SalesOrder())
    #print(con.query_product_dashboard())
    #con.logger.info("Test Report Message 2", type="report", key="Traceability")
    #print(con.query_product_movement_report())
    # print(con.query_traceability_report("BATCH-240526-A", "Executive Office Chair"))
    print(con.query_product_meter())
>>>>>>> dfcd0630c26e219a7187e71cd49a3531ad29663d
