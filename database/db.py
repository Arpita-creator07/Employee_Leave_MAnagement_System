import os
import sqlite3

import config


def get_connection():
    db_dir = os.path.dirname(config.DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT,
            email TEXT NOT NULL UNIQUE,
            department TEXT,
            job_role TEXT,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            attachment_path TEXT,
            admin_comment TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_policy (
            id INTEGER PRIMARY KEY,
            annual_days INTEGER NOT NULL,
            sick_days INTEGER NOT NULL,
            casual_days INTEGER NOT NULL,
            emergency_days INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO leave_policy
            (id, annual_days, sick_days, casual_days, emergency_days)
        VALUES
            (1, 20, 10, 5, 5)
    ''')

    admin_email = os.getenv('ADMIN_EMAIL', '').strip()
    admin_password = os.getenv('ADMIN_PASSWORD', '').strip()
    if admin_email and admin_password:
        cursor.execute('''
            INSERT OR IGNORE INTO users
                (name, email, department, job_role, password, role)
            VALUES
                (?, ?, ?, ?, ?, 'admin')
        ''', (
            os.getenv('ADMIN_NAME', 'Admin User').strip(),
            admin_email,
            os.getenv('ADMIN_DEPARTMENT', 'Administration').strip(),
            os.getenv('ADMIN_JOB_ROLE', 'Administrator').strip(),
            admin_password
        ))

    conn.commit()
    conn.close()
