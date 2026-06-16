from database.db import get_connection

def _ensure_attachment_column():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT COUNT(*)\n        FROM INFORMATION_SCHEMA.COLUMNS\n        WHERE TABLE_NAME='leaves' AND COLUMN_NAME='attachment_path'\n        ")
    exists = cursor.fetchone()[0]
    if not exists:
        cursor.execute('ALTER TABLE leaves ADD attachment_path NVARCHAR(500) NULL')
        conn.commit()
    conn.close()

def create_leave(user_id, type, start, end, reason, attachment_path=None):
    _ensure_attachment_column()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        INSERT INTO leaves(user_id,leave_type,start_date,end_date,reason,attachment_path)\n        VALUES(?,?,?,?,?,?)\n        ', (user_id, type, start, end, reason, attachment_path))
    conn.commit()
    conn.close()

def get_user_leaves(user_id):
    _ensure_attachment_column()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('\n        SELECT id,user_id,leave_type,start_date,end_date,reason,status,attachment_path,admin_comment\n        FROM leaves\n        WHERE user_id=?\n        ', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_dashboard_counts(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM leaves WHERE user_id=?', user_id)
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Approved' AND user_id=?", user_id)
    approved = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Rejected' AND user_id=?", user_id)
    rejected = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Pending' AND user_id=?", user_id)
    pending = cursor.fetchone()[0]
    conn.close()
    return (total, approved, rejected, pending)

def get_pending_requests():
    _ensure_attachment_column()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT leaves.id,users.name,leave_type,start_date,end_date,reason,status,attachment_path\n        FROM leaves\n        JOIN users ON leaves.user_id = users.id\n        WHERE status='Pending'\n    ")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_on_leave_today_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT COUNT(*)\n        FROM leaves\n        WHERE status='Approved'\n          AND CAST(GETDATE() AS date) BETWEEN CAST(start_date AS date) AND CAST(end_date AS date)\n    ")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_recent_requests(limit=5):
    limit = max(1, min(int(limit), 20))
    _ensure_attachment_column()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'\n        SELECT TOP {limit}\n            leaves.id,\n            users.name,\n            leaves.leave_type,\n            leaves.start_date,\n            leaves.end_date,\n            leaves.reason,\n            leaves.status,\n            leaves.attachment_path\n        FROM leaves\n        JOIN users ON leaves.user_id = users.id\n        ORDER BY leaves.id DESC\n    ')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_approved_leaves_for_calendar():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("\n        SELECT users.name, leaves.leave_type, leaves.start_date, leaves.end_date\n        FROM leaves\n        JOIN users ON leaves.user_id = users.id\n        WHERE leaves.status='Approved'\n        ORDER BY leaves.start_date ASC\n    ")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_admin_status_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM leaves')
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Approved'")
    approved = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leaves WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]
    conn.close()
    return (total, pending, approved, rejected)

def approve_leave(id, comment=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leaves SET status='Approved', admin_comment=? WHERE id=?", (comment, id))
    conn.commit()
    conn.close()

def reject_leave(id, comment):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leaves SET status='Rejected',admin_comment=? WHERE id=?", (comment, id))
    conn.commit()
    conn.close()
