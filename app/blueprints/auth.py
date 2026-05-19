from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User
from app.utils.md5 import md5_encrypt
from app.utils.decorators import login_required

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    # 如果已登录，直接跳转到对应首页
    if 'user_id' in session:
        return redirect_to_home(session['role'])
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # 表单验证
        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return render_template('auth/login.html')
        
        # 查询用户
        user = User.query.filter_by(username=username).first()
        
        # 验证用户和密码
        if not user or user.password != md5_encrypt(password):
            flash('用户名或密码错误', 'danger')
            return render_template('auth/login.html')
        
        # 登录成功，保存用户信息到session
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        flash('登录成功', 'success')
        return redirect_to_home(user.role)
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户退出"""
    session.clear()
    flash('您已安全退出系统', 'info')
    return redirect(url_for('auth_bp.login'))

def redirect_to_home(role: str):
    """根据角色跳转到对应首页"""
    if role == 'admin':
        return redirect(url_for('admin_bp.index'))
    elif role == 'teacher':
        return redirect(url_for('teacher_bp.index'))
    elif role == 'student':
        return redirect(url_for('student_bp.index'))
    else:
        return redirect(url_for('auth_bp.login'))
