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
    cursor.execute("""
        SELECT
            u.id,
            u.name,
            u.email,
            u.department,
            u.job_role,
            CAST(
                MAX(
                    ? - COALESCE(SUM(
                        CASE
                            WHEN l.status='Approved'
                            THEN julianday(l.end_date) - julianday(l.start_date) + 1
                            ELSE 0
                        END
                    ), 0),
                    0
                ) AS INTEGER
            ) AS leave_balance
        FROM users u
        LEFT JOIN leaves l ON l.user_id = u.id
        WHERE u.role = 'employee'
        GROUP BY u.id, u.name, u.email, u.department, u.job_role
        ORDER BY u.id DESC
        """, (annual_days,))
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
