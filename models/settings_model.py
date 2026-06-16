from database.db import get_connection

def _ensure_policy_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        IF OBJECT_ID('leave_policy', 'U') IS NULL\n        BEGIN\n            CREATE TABLE leave_policy (\n                id INT PRIMARY KEY,\n                annual_days INT NOT NULL,\n                sick_days INT NOT NULL,\n                casual_days INT NOT NULL,\n                emergency_days INT NOT NULL\n            )\n        END\n        ")
    conn.commit()
    conn.close()

def get_leave_policy():
    _ensure_policy_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        SELECT TOP 1 annual_days, sick_days, casual_days, emergency_days\n        FROM leave_policy\n        ORDER BY id\n        ')
    row = cursor.fetchone()
    if not row:
        cursor.execute('\n            INSERT INTO leave_policy(id, annual_days, sick_days, casual_days, emergency_days)\n            VALUES(1, 20, 10, 5, 5)\n            ')
        conn.commit()
        row = (20, 10, 5, 5)
    conn.close()
    return {'annual_days': row[0], 'sick_days': row[1], 'casual_days': row[2], 'emergency_days': row[3]}

def save_leave_policy(annual_days, sick_days, casual_days, emergency_days):
    _ensure_policy_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        IF EXISTS (SELECT 1 FROM leave_policy WHERE id = 1)\n            UPDATE leave_policy\n            SET annual_days = ?, sick_days = ?, casual_days = ?, emergency_days = ?\n            WHERE id = 1\n        ELSE\n            INSERT INTO leave_policy(id, annual_days, sick_days, casual_days, emergency_days)\n            VALUES(1, ?, ?, ?, ?)\n        ', (annual_days, sick_days, casual_days, emergency_days, annual_days, sick_days, casual_days, emergency_days))
    conn.commit()
    conn.close()
