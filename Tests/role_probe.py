# tools/quick_role_probe.py
# Run with:  python tools/quick_role_probe.py
import sys
from Database import Database

EMAIL_TO_CHECK = None  # e.g. "ahmad@gmail.com" or leave None to probe by EMP_ID
EMP_ID_TO_CHECK = 1    # fallback if EMAIL_TO_CHECK is None

db = Database.DatabaseConnection()
conn = getattr(db, "conn", None) or getattr(db, "connection", None)
if conn is None:
    print("Could not get DB connection from DatabaseConnection.")
    sys.exit(1)

cur = conn.cursor()

def one(sql, params=(), idx=None):
    try:
        cur.execute(sql, params)
        row = cur.fetchone()
        if row is None:
            return None
        return row if idx is None else row[idx]
    except Exception as e:
        return None

def get_emp_id(email):
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
    # Try project helper if present
    if hasattr(db, "query_employee_login"):
        try:
            val = db.query_employee_login(email)
            if val is not None:
                return int(val)
        except Exception:
            pass
    return None

def get_name(emp_id):
    tries = [
        ("SELECT employeeName FROM Workers WHERE employeeID=?", (emp_id,), 0),
        ("SELECT EmployeeName FROM Workers WHERE EmployeeID=?", (emp_id,), 0),
        ("SELECT name FROM Employees WHERE id=?", (emp_id,), 0),
    ]
    for sql, params, idx in tries:
        val = one(sql, params, idx)
        if val:
            return str(val)
    return None

def get_role_join(emp_id):
    # returns (role_id, role_name)
    tries = [
        ("SELECT w.roleID, r.role_name FROM Workers w JOIN Roles r ON w.roleID=r.role_id WHERE w.employeeID=?",
         (emp_id,), (0, 1)),
        ("SELECT w.RoleID, r.RoleName FROM Workers w JOIN Roles r ON w.RoleID=r.RoleID WHERE w.EmployeeID=?",
         (emp_id,), (0, 1)),
        ("SELECT a.role_id, r.role_name FROM Accounts a JOIN Roles r ON a.role_id=r.role_id WHERE a.employee_id=?",
         (emp_id,), (0, 1)),
        ("SELECT a.RoleID, r.RoleName FROM Accounts a JOIN Roles r ON a.RoleID=r.RoleID WHERE a.EmployeeID=?",
         (emp_id,), (0, 1)),
    ]
    for sql, params, idxs in tries:
        try:
            cur.execute(sql, params)
            row = cur.fetchone()
            if row and row[idxs[0]] is not None:
                return (int(row[idxs[0]]), str(row[idxs[1]]) if row[idxs[1]] is not None else None)
        except Exception:
            continue
    # text fallback
    txt = one("SELECT role FROM Workers WHERE employeeID=?", (emp_id,), 0) \
          or one("SELECT Role FROM Workers WHERE EmployeeID=?", (emp_id,), 0) \
          or one("SELECT position FROM Workers WHERE employeeID=?", (emp_id,), 0)
    return (None, str(txt) if txt else None)

def list_roles():
    out = []
    tries = [
        ("SELECT role_id, role_name FROM Roles", (), (0, 1)),
        ("SELECT RoleID, RoleName FROM Roles", (), (0, 1)),
        ("SELECT id, name FROM roles", (), (0, 1)),
    ]
    for sql, params, idxs in tries:
        try:
            cur.execute(sql, params)
            for row in cur.fetchall():
                out.append((row[idxs[0]], row[idxs[1]]))
            break
        except Exception:
            continue
    return out

if EMAIL_TO_CHECK:
    emp_id = get_emp_id(EMAIL_TO_CHECK)
else:
    emp_id = EMP_ID_TO_CHECK

print("=== QUICK ROLE PROBE ===")
print("Email:", EMAIL_TO_CHECK)
print("EmployeeID:", emp_id)

if emp_id is None:
    print("Could not resolve employee id. Check the email or Accounts/Workers mapping.")
    sys.exit(0)

print("Name:", get_name(emp_id))
rid, rname = get_role_join(emp_id)
print("RoleID:", rid)
print("RoleName:", rname)
print("\nAll Roles in DB:")
for rid2, rn in list_roles():
    print(" -", rid2, rn)

cur.close()
