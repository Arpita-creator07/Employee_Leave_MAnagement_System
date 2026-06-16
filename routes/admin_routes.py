from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from datetime import datetime
from models.leave_model import *
from models.settings_model import get_leave_policy, save_leave_policy
from models.user_model import create_employee_admin, get_employee_directory, get_total_employees, get_user_by_id
from models.user_model import get_user_by_email
from utils.validation import validate_email, validate_name, validate_password
admin_bp = Blueprint('admin', __name__)

def _word_count(text):
    return len([w for w in (text or '').strip().split() if w])

def _date_to_iso(value):
    if value is None:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d')
    text = str(value).strip()
    return text[:10] if len(text) >= 10 else text

def _build_calendar_items():
    items = []
    for row in get_approved_leaves_for_calendar():
        items.append({'employee': row[0], 'leave_type': row[1], 'start_date': _date_to_iso(row[2]), 'end_date': _date_to_iso(row[3])})
    return items

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    now = datetime.now()
    date_display = f"{now.strftime('%A, %B')} {now.day}, {now.year}"
    leave_policy = get_leave_policy()
    pending_requests = get_pending_requests()
    total_requests, pending_total, approved_total, rejected_total = get_admin_status_counts()
    admin_user = get_user_by_id(session.get('user_id'))
    admin_name = admin_user[1] if admin_user else 'Admin User'
    admin_email = admin_user[2] if admin_user else 'admin@example.com'
    admin_role = admin_user[3] if admin_user else 'admin'
    admin_job_role = admin_user[5] if admin_user and len(admin_user) > 5 else 'Administrator'
    admin_initials = ''.join([part[0].upper() for part in admin_name.split()[:2]]) if admin_name else 'A'
    add_status = request.args.get('add_status')
    add_message = request.args.get('add_message')
    action_status = request.args.get('action_status')
    action_message = request.args.get('action_message')
    settings_status = request.args.get('settings_status')
    settings_message = request.args.get('settings_message')
    active_tab = request.args.get('tab', 'dashboard')
    settings_form = {'annual_days': request.args.get('annual_days', ''), 'sick_days': request.args.get('sick_days', ''), 'casual_days': request.args.get('casual_days', ''), 'emergency_days': request.args.get('emergency_days', '')}
    return render_template('admin_dashboard.html', date_display=date_display, admin_name=admin_name, admin_email=admin_email, admin_role=admin_role, admin_job_role=admin_job_role, admin_initials=admin_initials, leave_policy=leave_policy, settings_form=settings_form, active_tab=active_tab, add_status=add_status, add_message=add_message, action_status=action_status, action_message=action_message, settings_status=settings_status, settings_message=settings_message, total_employees=get_total_employees(), on_leave_today=get_on_leave_today_count(), pending_count=pending_total, total_requests=total_requests, approved_count=approved_total, rejected_count=rejected_total, pending_requests=pending_requests, recent_requests=get_recent_requests(8), employees=get_employee_directory(leave_policy['annual_days']), calendar_leaves=_build_calendar_items())

@admin_bp.route('/admin/calendar')
def admin_calendar():
    if session.get('role') != 'admin':
        return (jsonify({'error': 'Unauthorized'}), 401)
    return jsonify({'calendar': _build_calendar_items()})

@admin_bp.route('/admin/pending')
def pending():
    data = get_pending_requests()
    return jsonify({'pending': str(data)})

@admin_bp.route('/admin/employees/add', methods=['POST'])
def add_employee():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip()
    department = (request.form.get('department') or '').strip()
    job_role = (request.form.get('job_role') or '').strip()
    password = (request.form.get('password') or '').strip()
    if not all([name, email, department, job_role, password]):
        return redirect(url_for('admin.admin_dashboard', add_status='error', add_message='All fields are required'))
    ok, message, clean_name = validate_name(name)
    if not ok:
        return redirect(url_for('admin.admin_dashboard', add_status='error', add_message=message, tab='employees'))
    ok, message, clean_email = validate_email(email)
    if not ok:
        return redirect(url_for('admin.admin_dashboard', add_status='error', add_message=message, tab='employees'))
    ok, message = validate_password(password)
    if not ok:
        return redirect(url_for('admin.admin_dashboard', add_status='error', add_message=message, tab='employees'))
    if get_user_by_email(clean_email):
        return redirect(url_for('admin.admin_dashboard', add_status='error', add_message='Email is already registered', tab='employees'))
    try:
        create_employee_admin(clean_name, clean_email, department, job_role, password)
    except Exception:
        return redirect(url_for('admin.admin_dashboard', add_status='error', add_message='Unable to add employee'))
    return redirect(url_for('admin.admin_dashboard', add_status='success', add_message='Employee added successfully', tab='employees'))

@admin_bp.route('/admin/settings/save', methods=['POST'])
def save_settings():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    annual_raw = (request.form.get('annual_days') or '').strip()
    sick_raw = (request.form.get('sick_days') or '').strip()
    casual_raw = (request.form.get('casual_days') or '').strip()
    emergency_raw = (request.form.get('emergency_days') or '').strip()

    def error_redirect(message):
        return redirect(url_for('admin.admin_dashboard', tab='settings', settings_status='error', settings_message=message, annual_days=annual_raw, sick_days=sick_raw, casual_days=casual_raw, emergency_days=emergency_raw))
    try:
        annual_days = int(annual_raw)
        sick_days = int(sick_raw)
        casual_days = int(casual_raw)
        emergency_days = int(emergency_raw)
    except ValueError:
        return error_redirect('All leave values must be numbers')
    if min(annual_days, sick_days, casual_days, emergency_days) < 0:
        return error_redirect('Leave values cannot be negative')
    total_breakdown = sick_days + casual_days + emergency_days
    if total_breakdown != annual_days:
        return error_redirect('Sick + Casual + Emergency leave must be exactly equal to Annual leave')
    save_leave_policy(annual_days, sick_days, casual_days, emergency_days)
    return redirect(url_for('admin.admin_dashboard', tab='settings', settings_status='success', settings_message='Settings saved successfully'))

@admin_bp.route('/admin/approve/<int:id>', methods=['POST'])
def approve(id):
    if session.get('role') != 'admin':
        if request.is_json:
            return (jsonify({'error': 'Unauthorized'}), 401)
        return redirect(url_for('home'))
    comment = None
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        comment = (payload.get('comment') or '').strip()
    else:
        comment = (request.form.get('comment') or '').strip()
    approve_leave(id, comment if comment else None)
    if request.is_json:
        return jsonify({'message': 'Leave approved'})
    return redirect(url_for('admin.admin_dashboard', tab='dashboard', action_status='success', action_message='Leave approved'))

@admin_bp.route('/admin/reject/<int:id>', methods=['POST'])
def reject(id):
    if session.get('role') != 'admin':
        if request.is_json:
            return (jsonify({'error': 'Unauthorized'}), 401)
        return redirect(url_for('home'))
    comment = None
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        comment = payload.get('comment')
    else:
        comment = request.form.get('comment')
    comment = (comment or '').strip()
    if not comment:
        if request.is_json:
            return (jsonify({'error': 'Comment required'}), 400)
        return redirect(url_for('admin.admin_dashboard', tab='dashboard', action_status='error', action_message='Comment is required for rejection'))
    if _word_count(comment) < 5:
        if request.is_json:
            return (jsonify({'error': 'Rejection comment must be at least 5 words'}), 400)
        return redirect(url_for('admin.admin_dashboard', tab='dashboard', action_status='error', action_message='Rejection comment must be at least 5 words'))
    reject_leave(id, comment)
    if request.is_json:
        return jsonify({'message': 'Leave rejected'})
    return redirect(url_for('admin.admin_dashboard', tab='dashboard', action_status='success', action_message='Leave rejected'))
