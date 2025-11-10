# tools/set_role_by_name.py
# Run with:  python tools/set_role_by_name.py
TARGET_EMAIL = "ahmad@gmail.com"  # change me
TARGET_ROLE_NAME = "Admin"   # change me ("Worker" / "Supervisor" / etc.)
# --- path shim so imports like "from Database import Database" work ---
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ----------------------------------------------------------------------

from Database import Database

import Database
from Database.Database import DatabaseConnection

db = Database.DatabaseConnection()
conn = getattr(db, "conn", None) or getattr(db, "connection", None)
if conn is None:
    print("Could not get DB connection from DatabaseConnection.")
    raise SystemExit(1)

cur = conn.cursor()

def one(sql, params=(), idx=None):
    try:
        cur.execute(sql, params)
        row = cur.fetchone()
        if row is None:
            return None
        return row if idx is None else row[idx]
    except Exception:
        return None

def get_emp_id_by_email(email):
    tries = [
        ("SELECT employee_id FROM Accounts WHERE LOWER(email)=LOWER(?)", (email,), 0),
        ("SELECT EmployeeID FROM Accounts WHERE LOWER(Email)=LOWER(?)", (email,), 0),
        ("SELECT employeeID FROM Workers WHERE LOWER(email)=LOWER(?)", (email,), 0),
        ("SELECT EmployeeID FROM Workers WHERE LOWER(Email)=LOWER(?)", (email,), 0),
    ]
    for sql, params, idx in tries:
        val = one(sql, params, idx)
        if val is not None:
            return int(val)
    if hasattr(db, "query_employee_login"):
        try:
            val = db.query_employee_login(email)
            if val is not None:
                return int(val)
        except Exception:
            pass
    return None

def resolve_role_id(role_name):
    tries = [
        ("SELECT role_id FROM Roles WHERE LOWER(role_name)=LOWER(?)", (role_name,), 0),
        ("SELECT RoleID FROM Roles WHERE LOWER(RoleName)=LOWER(?)", (role_name,), 0),
        ("SELECT id FROM roles WHERE LOWER(name)=LOWER(?)", (role_name,), 0),
    ]
    for sql, params, idx in tries:
        val = one(sql, params, idx)
        if val is not None:
            return int(val)
    return None

emp_id = get_emp_id_by_email(TARGET_EMAIL)
if emp_id is None:
    print("Could not find employee for email:", TARGET_EMAIL)
    raise SystemExit(1)

role_id = resolve_role_id(TARGET_ROLE_NAME)
if role_id is None:
    print("Could not find role:", TARGET_ROLE_NAME)
    raise SystemExit(1)

print(f"Setting EmployeeID={emp_id} to role '{TARGET_ROLE_NAME}' (RoleID={role_id})")

# Try updating Workers first
updated = False
tries = [
    ("UPDATE Workers SET roleID=? WHERE employeeID=?", (role_id, emp_id)),
    ("UPDATE Workers SET RoleID=? WHERE EmployeeID=?", (role_id, emp_id)),
]
for sql, params in tries:
    try:
        cur.execute(sql, params)
        if cur.rowcount:
            updated = True
            print("Updated Workers table.")
            break
    except Exception:
        continue

# Also update Accounts if that table owns the role mapping
tries = [
    ("UPDATE Accounts SET role_id=? WHERE employee_id=?", (role_id, emp_id)),
    ("UPDATE Accounts SET RoleID=? WHERE EmployeeID=?", (role_id, emp_id)),
]
for sql, params in tries:
    try:
        cur.execute(sql, params)
        if cur.rowcount:
            updated = True
            print("Updated Accounts table.")
            break
    except Exception:
        continue

if not updated:
    print("No rows updated. Check which table stores the role mapping in your schema.")
else:
    try:
        conn.commit()
        print("Committed changes.")
    except Exception as e:
        print("Commit failed:", e)

cur.close()
