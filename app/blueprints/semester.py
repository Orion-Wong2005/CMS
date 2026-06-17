from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Semester
from app.utils.decorators import admin_required
from datetime import datetime

semester_bp = Blueprint('semester_bp', __name__, url_prefix='/semester')

@semester_bp.route('/')
@admin_required
def semester_list():
    semesters = Semester.query.order_by(Semester.year_start.desc(), Semester.semester_num.desc()).all()
    return render_template('semester/semester_list.html', semesters=semesters)

@semester_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def semester_add():
    # 获取服务器本地时间
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 根据当前月份推断学期
    # 第1学期（秋季）：9月-次年1月
    # 第2学期（春季）：2月-6月
    # 第3学期（暑期）：7月-8月
    if current_month >= 9 or current_month <= 1:
        year_start = current_year if current_month >= 9 else current_year - 1
        year_end = year_start + 1
        default_semester = 1 if current_month >= 9 else 2
    elif current_month >= 2 and current_month <= 6:
        year_start = current_year - 1
        year_end = current_year
        default_semester = 2
    else:  # 7-8月
        year_start = current_year
        year_end = current_year + 1
        default_semester = 3
    
    if request.method == 'POST':
        year_start = request.form.get('year_start', type=int)
        year_end = request.form.get('year_end', type=int)
        semester_num = request.form.get('semester_num', type=int)
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        
        # 验证
        if not year_start or not year_end or not semester_num:
            flash('请填写所有必填字段', 'danger')
            return render_template('semester/semester_form.html', 
                                   current_year=current_year,
                                   year_start=year_start,
                                   year_end=year_end,
                                   default_semester=semester_num)
        
        if semester_num < 1 or semester_num > 3:
            flash('学期序号只能是1、2或3', 'danger')
            return render_template('semester/semester_form.html', 
                                   current_year=current_year,
                                   year_start=year_start,
                                   year_end=year_end,
                                   default_semester=semester_num)
        
        # 检查是否已存在
        existing = Semester.query.filter_by(
            year_start=year_start,
            year_end=year_end,
            semester_num=semester_num
        ).first()
        if existing:
            flash('该学期已存在', 'danger')
            return render_template('semester/semester_form.html', 
                                   current_year=current_year,
                                   year_start=year_start,
                                   year_end=year_end,
                                   default_semester=semester_num)
        
        # 解析日期
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except:
                flash('日期格式不正确', 'danger')
                return render_template('semester/semester_form.html', 
                                       current_year=current_year,
                                       year_start=year_start,
                                       year_end=year_end,
                                       default_semester=semester_num)
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except:
                flash('日期格式不正确', 'danger')
                return render_template('semester/semester_form.html', 
                                       current_year=current_year,
                                       year_start=year_start,
                                       year_end=year_end,
                                       default_semester=semester_num)
        
        try:
            semester = Semester(
                year_start=year_start,
                year_end=year_end,
                semester_num=semester_num,
                start_date=start_date,
                end_date=end_date,
                status=1
            )
            db.session.add(semester)
            db.session.commit()
            flash('学期添加成功', 'success')
            return redirect(url_for('semester_bp.semester_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('semester/semester_form.html', 
                           current_year=current_year,
                           year_start=year_start,
                           year_end=year_end,
                           default_semester=default_semester)

@semester_bp.route('/delete/<int:semester_id>')
@admin_required
def semester_delete(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    try:
        db.session.delete(semester)
        db.session.commit()
        flash('学期删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    return redirect(url_for('semester_bp.semester_list'))

@semester_bp.route('/toggle/<int:semester_id>')
@admin_required
def semester_toggle(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    semester.status = 0 if semester.status == 1 else 1
    try:
        db.session.commit()
        status_text = '开启' if semester.status == 1 else '关闭'
        flash(f'学期已{status_text}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'操作失败：{str(e)}', 'danger')
    return redirect(url_for('semester_bp.semester_list'))
