from database.db import get_connection


def get_leave_policy():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT annual_days, sick_days, casual_days, emergency_days
        FROM leave_policy
        WHERE id = 1
    ''')
    row = cursor.fetchone()
    if not row:
        cursor.execute('''
            INSERT INTO leave_policy(id, annual_days, sick_days, casual_days, emergency_days)
            VALUES(1, 20, 10, 5, 5)
        ''')
        conn.commit()
        row = (20, 10, 5, 5)
    conn.close()
    return {
        'annual_days': row[0],
        'sick_days': row[1],
        'casual_days': row[2],
        'emergency_days': row[3]
    }


def save_leave_policy(annual_days, sick_days, casual_days, emergency_days):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leave_policy(id, annual_days, sick_days, casual_days, emergency_days)
        VALUES(1, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            annual_days = excluded.annual_days,
            sick_days = excluded.sick_days,
            casual_days = excluded.casual_days,
            emergency_days = excluded.emergency_days
    ''', (annual_days, sick_days, casual_days, emergency_days))
    conn.commit()
    conn.close()
