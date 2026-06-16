from datetime import date, datetime
import os
import uuid
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from models.leave_model import create_leave, get_user_leaves
from models.settings_model import get_leave_policy
from models.user_model import get_user_by_email, get_user_by_id, update_employee_profile
employee_bp = Blueprint('employee', __name__)
ALLOWED_ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    return None

def _leave_days(start, end):
    start_date = _to_date(start)
    end_date = _to_date(end)
    if not start_date or not end_date:
        return 0
    return max((end_date - start_date).days + 1, 0)

def _word_count(text):
    return len([w for w in (text or '').strip().split() if w])

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_ATTACHMENT_EXTENSIONS

@employee_bp.route('/employee/dashboard')
def employee_dashboard():
    if session.get('role') != 'employee':
        return redirect(url_for('home'))
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    policy = get_leave_policy()
    leaves = get_user_leaves(user_id)
    used_days = {'annual': 0, 'sick': 0, 'casual': 0, 'emergency': 0}
    for row in leaves:
        leave_type = (row[2] or '').lower()
        status = (row[6] or '').lower()
        if status != 'approved':
            continue
        used_units = 1
        used_days['annual'] += used_units
        if leave_type == 'sick leave':
            used_days['sick'] += used_units
        elif leave_type == 'casual leave':
            used_days['casual'] += used_units
        elif leave_type == 'emergency leave':
            used_days['emergency'] += used_units
    totals = {'annual': policy['annual_days'], 'sick': policy['sick_days'], 'casual': policy['casual_days'], 'emergency': policy['emergency_days']}
    balances = {key: max(totals[key] - used_days[key], 0) for key in totals}
    display_leaves = sorted(leaves, key=lambda r: r[0], reverse=True)
    leave_items = []
    for row in display_leaves:
        days = _leave_days(row[3], row[4])
        leave_items.append({'id': row[0], 'type': row[2], 'start': str(row[3]) if row[3] else '', 'end': str(row[4]) if row[4] else '', 'reason': row[5] or '', 'status': row[6] or '', 'attachment_path': row[7] or '', 'admin_comment': row[8] or '', 'days': days})
    recent_leaves = leave_items[:5]
    employee_name = user[1] if user else 'Employee'
    employee_email = user[2] if user else ''
    employee_department = user[4] if user and len(user) > 4 else ''
    employee_job_role = user[5] if user and len(user) > 5 else ''
    initials = ''.join([part[0].upper() for part in employee_name.split()[:2]]) if employee_name else 'E'
    profile_status = request.args.get('profile_status')
    profile_message = request.args.get('profile_message')
    profile_form = {'name': request.args.get('name', employee_name), 'email': request.args.get('email', employee_email)}
    return render_template('employee_dashboard.html', employee_name=employee_name, employee_email=employee_email, employee_initials=initials, employee_department=employee_department, employee_job_role=employee_job_role, leave_totals=totals, leave_used=used_days, leave_balance=balances, my_leaves=leave_items, recent_leaves=recent_leaves, profile_status=profile_status, profile_message=profile_message, profile_form=profile_form)

@employee_bp.route('/employee/profile/update', methods=['POST'])
def update_profile():
    if session.get('role') != 'employee':
        return redirect(url_for('home'))
    user_id = session.get('user_id')
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip()

    def redirect_error(message):
        return redirect(url_for('employee.employee_dashboard', tab='settings', profile_status='error', profile_message=message, name=name, email=email))
    if not name or not email:
        return redirect_error('Name and email are required')
    if '@' not in email or '.' not in email.split('@')[-1]:
        return redirect_error('Please enter a valid email address')
    existing_user = get_user_by_email(email)
    if existing_user and existing_user[0] != user_id:
        return redirect_error('Email is already in use')
    update_employee_profile(user_id, name, email)
    return redirect(url_for('employee.employee_dashboard', tab='settings', profile_status='success', profile_message='Profile updated successfully'))

@employee_bp.route('/apply_leave', methods=['POST'])
def apply():
    if session.get('role') != 'employee':
        return (jsonify({'error': 'Unauthorized'}), 401)
    if request.content_type and 'multipart/form-data' in request.content_type:
        payload = request.form
    else:
        payload = request.get_json(silent=True) or {}
    leave_type = (payload.get('leave_type') or '').strip()
    start_date_raw = (payload.get('start_date') or '').strip()
    end_date_raw = (payload.get('end_date') or '').strip()
    reason = (payload.get('reason') or '').strip()
    if not all([leave_type, start_date_raw, end_date_raw, reason]):
        return (jsonify({'error': 'All fields are required'}), 400)
    try:
        start_date = datetime.fromisoformat(start_date_raw).date()
        end_date = datetime.fromisoformat(end_date_raw).date()
    except ValueError:
        return (jsonify({'error': 'Invalid date format'}), 400)
    today = date.today()
    if start_date < today or end_date < today:
        return (jsonify({'error': 'Start date and end date cannot be in the past'}), 400)
    if start_date >= end_date:
        return (jsonify({'error': 'Start date and end date cannot be same; end date must be after start date'}), 400)
    words = _word_count(reason)
    if words < 50 or words > 200:
        return (jsonify({'error': 'Reason must be between 50 and 200 words'}), 400)
    attachment_path = None
    upload_file = request.files.get('attachment')
    if upload_file and upload_file.filename:
        filename = secure_filename(upload_file.filename)
        if not _allowed_file(filename):
            return (jsonify({'error': 'Invalid attachment type. Allowed: PDF, DOC, DOCX, JPG, JPEG, PNG'}), 400)
        extension = filename.rsplit('.', 1)[1].lower()
        generated_name = f'{uuid.uuid4().hex}.{extension}'
        upload_dir = os.path.join('static', 'uploads', 'leave_docs')
        os.makedirs(upload_dir, exist_ok=True)
        abs_path = os.path.join(upload_dir, generated_name)
        upload_file.save(abs_path)
        attachment_path = f'/static/uploads/leave_docs/{generated_name}'
    create_leave(session.get('user_id'), leave_type, start_date_raw, end_date_raw, reason, attachment_path)
    return jsonify({'message': 'Leave applied'})

@employee_bp.route('/my_leaves/<int:user_id>')
def my_leaves(user_id):
    leaves = get_user_leaves(user_id)
    return jsonify({'leaves': str(leaves)})


