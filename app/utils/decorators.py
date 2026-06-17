from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 判断是否是API请求（期望JSON响应）
            if request.path.endswith('/data') or request.accept_mimetypes.accept_json:
                from flask import jsonify
                return jsonify({'error': '请先登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            if request.path.endswith('/data') or request.accept_mimetypes.accept_json:
                from flask import jsonify
                return jsonify({'error': '您没有管理员权限'}), 403
            flash('您没有管理员权限', 'danger')
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'teacher':
            if request.path.endswith('/data') or request.accept_mimetypes.accept_json:
                from flask import jsonify
                return jsonify({'error': '您没有教师权限'}), 403
            flash('您没有教师权限', 'danger')
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'student':
            if request.path.endswith('/data') or request.accept_mimetypes.accept_json:
                from flask import jsonify
                return jsonify({'error': '您没有学生权限'}), 403
            flash('您没有学生权限', 'danger')
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function
