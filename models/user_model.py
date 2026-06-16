from database.db import get_connection

def create_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users(username,email,password,role) VALUES(?,?,?,?)', (username, email, password, 'employee'))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_total_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='employee'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_employee_directory(annual_days=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT\n            u.id,\n            u.name,\n            u.email,\n            u.department,\n            u.job_role,\n            CASE\n                WHEN ? - ISNULL(SUM(\n                    CASE\n                        WHEN l.status='Approved'\n                        THEN DATEDIFF(day, CAST(l.start_date AS date), CAST(l.end_date AS date)) + 1\n                        ELSE 0\n                    END\n                ), 0) < 0 THEN 0\n                ELSE ? - ISNULL(SUM(\n                    CASE\n                        WHEN l.status='Approved'\n                        THEN DATEDIFF(day, CAST(l.start_date AS date), CAST(l.end_date AS date)) + 1\n                        ELSE 0\n                    END\n                ), 0)\n            END AS leave_balance\n        FROM users u\n        LEFT JOIN leaves l ON l.user_id = u.id\n        WHERE u.role = 'employee'\n        GROUP BY u.id, u.name, u.email, u.department, u.job_role\n        ORDER BY u.id DESC\n        ", (annual_days, annual_days))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, role, department, job_role FROM users WHERE id=?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_employee_profile(user_id, name, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        UPDATE users\n        SET name=?, email=?\n        WHERE id=? AND role='employee'\n        ", (name, email, user_id))
    conn.commit()
    conn.close()

def create_employee_admin(name, email, department, job_role, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        INSERT INTO users(name,email,department,job_role,password,role)\n        VALUES(?,?,?,?,?,?)\n        ', (name, email, department, job_role, password, 'employee'))
    conn.commit()
    conn.close()
