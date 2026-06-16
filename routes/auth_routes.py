from flask import Blueprint, render_template, request, redirect, session, url_for
from database.db import get_connection
from models.user_model import get_user_by_email
from utils.validation import validate_email, validate_name, validate_password
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', status=None, message=None, form_data={})
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip()
    department = (request.form.get('department') or '').strip()
    job_role = (request.form.get('job_role') or '').strip()
    password = (request.form.get('password') or '').strip()
    form_data = {'name': name, 'email': email, 'department': department, 'job_role': job_role}
    if not all([name, email, department, job_role, password]):
        return render_template('register.html', status='error', message='All fields are required.', form_data=form_data)
    ok, message, clean_name = validate_name(name)
    if not ok:
        form_data['name'] = clean_name
        return render_template('register.html', status='error', message=message, form_data=form_data)
    ok, message, clean_email = validate_email(email)
    if not ok:
        form_data['email'] = clean_email
        return render_template('register.html', status='error', message=message, form_data=form_data)
    ok, message = validate_password(password)
    if not ok:
        return render_template('register.html', status='error', message=message, form_data=form_data)
    if get_user_by_email(clean_email):
        form_data['name'] = clean_name
        form_data['email'] = clean_email
        return render_template('register.html', status='error', message='Email is already registered.', form_data=form_data)
    query = '\n    INSERT INTO users (name,email,department,job_role,password,role)\n    VALUES (?,?,?,?,?,?)\n    '
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (clean_name, clean_email, department, job_role, password, 'employee'))
        conn.commit()
        conn.close()
    except Exception:
        return render_template('register.html', status='error', message='Unable to register user. Please try again.', form_data=form_data)
    return redirect(url_for('home'))

@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True) or {}
    email = request.form.get('email') or payload.get('email')
    password = request.form.get('password') or payload.get('password')
    if not email or not password:
        return ('Email and password are required', 400)
    query = 'SELECT id, role FROM users WHERE email=? AND password=?'
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        role = user[1]
        session['user_id'] = user[0]
        session['role'] = role
        if role == 'admin':
            return redirect(url_for('admin.admin_dashboard', tab='dashboard'))
        else:
            return redirect('/employee/dashboard')
    return 'Invalid Login'

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
