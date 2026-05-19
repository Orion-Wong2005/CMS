from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import User, Student, Teacher, Course, Schedule
from app.utils.decorators import admin_required
from app.utils.md5 import md5_encrypt

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# ==============================
# 管理员首页
# ==============================
@admin_bp.route('/')
@admin_required
def index():
    """管理员首页 - 数据统计面板"""
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    course_count = Course.query.count()
    
    return render_template('admin/index.html',
                          student_count=student_count,
                          teacher_count=teacher_count,
                          course_count=course_count)

# ==============================
# 学生管理
# ==============================
@admin_bp.route('/students')
@admin_required
def student_list():
    """学生列表"""
    students = Student.query.all()
    return render_template('admin/student_list.html', students=students)

@admin_bp.route('/students/add', methods=['GET', 'POST'])
@admin_required
def student_add():
    """添加学生"""
    if request.method == 'POST':
        # 获取表单数据
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        major = request.form.get('major', '').strip()
        class_name = request.form.get('class_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        
        # 表单验证
        if not student_id or not name:
            flash('学号和姓名不能为空', 'danger')
            return render_template('admin/student_form.html')
        
        # 检查学号是否已存在
        if Student.query.get(student_id):
            flash('该学号已存在', 'danger')
            return render_template('admin/student_form.html')
        
        try:
            # 创建用户账号(默认密码为学号)
            user = User(
                username=student_id,
                password=md5_encrypt(student_id),
                role='student'
            )
            db.session.add(user)
            db.session.flush()  # 获取user.id
            
            # 创建学生信息
            student = Student(
                student_id=student_id,
                name=name,
                gender=gender,
                major=major,
                class_name=class_name,
                phone=phone,
                email=email,
                user_id=user.id
            )
            db.session.add(student)
            db.session.commit()
            
            flash('学生添加成功！默认登录密码为学号', 'success')
            return redirect(url_for('admin_bp.student_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('admin/student_form.html')

@admin_bp.route('/students/edit/<string:student_id>', methods=['GET', 'POST'])
@admin_required
def student_edit(student_id):
    """编辑学生"""
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        # 更新学生信息
        student.name = request.form.get('name', '').strip()
        student.gender = request.form.get('gender', '').strip()
        student.major = request.form.get('major', '').strip()
        student.class_name = request.form.get('class_name', '').strip()
        student.phone = request.form.get('phone', '').strip()
        student.email = request.form.get('email', '').strip()
        
        try:
            db.session.commit()
            flash('学生信息更新成功', 'success')
            return redirect(url_for('admin_bp.student_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('admin/student_form.html', student=student)

@admin_bp.route('/students/delete/<string:student_id>')
@admin_required
def student_delete(student_id):
    """删除学生"""
    student = Student.query.get_or_404(student_id)
    
    try:
        # 级联删除：会同时删除对应的用户、选课、成绩
        db.session.delete(student)
        db.session.commit()
        flash('学生删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.student_list'))

# ==============================
# 教师管理
# ==============================
@admin_bp.route('/teachers')
@admin_required
def teacher_list():
    """教师列表"""
    teachers = Teacher.query.all()
    return render_template('admin/teacher_list.html', teachers=teachers)

@admin_bp.route('/teachers/add', methods=['GET', 'POST'])
@admin_required
def teacher_add():
    """添加教师"""
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id', '').strip()
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        department = request.form.get('department', '').strip()
        title = request.form.get('title', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        
        if not teacher_id or not name:
            flash('工号和姓名不能为空', 'danger')
            return render_template('admin/teacher_form.html')
        
        if Teacher.query.get(teacher_id):
            flash('该工号已存在', 'danger')
            return render_template('admin/teacher_form.html')
        
        try:
            # 创建用户账号(默认密码为工号)
            user = User(
                username=teacher_id,
                password=md5_encrypt(teacher_id),
                role='teacher'
            )
            db.session.add(user)
            db.session.flush()
            
            # 创建教师信息
            teacher = Teacher(
                teacher_id=teacher_id,
                name=name,
                gender=gender,
                department=department,
                title=title,
                phone=phone,
                email=email,
                user_id=user.id
            )
            db.session.add(teacher)
            db.session.commit()
            
            flash('教师添加成功！默认登录密码为工号', 'success')
            return redirect(url_for('admin_bp.teacher_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('admin/teacher_form.html')

@admin_bp.route('/teachers/edit/<string:teacher_id>', methods=['GET', 'POST'])
@admin_required
def teacher_edit(teacher_id):
    """编辑教师"""
    teacher = Teacher.query.get_or_404(teacher_id)
    
    if request.method == 'POST':
        teacher.name = request.form.get('name', '').strip()
        teacher.gender = request.form.get('gender', '').strip()
        teacher.department = request.form.get('department', '').strip()
        teacher.title = request.form.get('title', '').strip()
        teacher.phone = request.form.get('phone', '').strip()
        teacher.email = request.form.get('email', '').strip()
        
        try:
            db.session.commit()
            flash('教师信息更新成功', 'success')
            return redirect(url_for('admin_bp.teacher_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('admin/teacher_form.html', teacher=teacher)

@admin_bp.route('/teachers/delete/<string:teacher_id>')
@admin_required
def teacher_delete(teacher_id):
    """删除教师"""
    teacher = Teacher.query.get_or_404(teacher_id)
    
    try:
        db.session.delete(teacher)
        db.session.commit()
        flash('教师删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：该教师可能有授课课程', 'danger')
    
    return redirect(url_for('admin_bp.teacher_list'))

# ==============================
# 课程管理
# ==============================
@admin_bp.route('/courses')
@admin_required
def course_list():
    """课程列表"""
    courses = Course.query.all()
    return render_template('admin/course_list.html', courses=courses)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@admin_required
def course_add():
    """添加课程"""
    teachers = Teacher.query.all()
    
    if request.method == 'POST':
        course_id = request.form.get('course_id', '').strip()
        course_name = request.form.get('course_name', '').strip()
        credit = request.form.get('credit', '').strip()
        hours = request.form.get('hours', '').strip()
        teacher_id = request.form.get('teacher_id', '').strip()
        semester = request.form.get('semester', '').strip()
        capacity = request.form.get('capacity', 60)
        
        if not course_id or not course_name or not credit or not hours:
            flash('课程编号、名称、学分、学时不能为空', 'danger')
            return render_template('admin/course_form.html', teachers=teachers)
        
        if Course.query.get(course_id):
            flash('该课程编号已存在', 'danger')
            return render_template('admin/course_form.html', teachers=teachers)
        
        try:
            course = Course(
                course_id=course_id,
                course_name=course_name,
                credit=float(credit),
                hours=int(hours),
                teacher_id=teacher_id if teacher_id else None,
                semester=semester,
                capacity=int(capacity)
            )
            db.session.add(course)
            db.session.commit()
            
            flash('课程添加成功', 'success')
            return redirect(url_for('admin_bp.course_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('admin/course_form.html', teachers=teachers)

@admin_bp.route('/courses/edit/<string:course_id>', methods=['GET', 'POST'])
@admin_required
def course_edit(course_id):
    """编辑课程"""
    course = Course.query.get_or_404(course_id)
    teachers = Teacher.query.all()
    
    if request.method == 'POST':
        course.course_name = request.form.get('course_name', '').strip()
        course.credit = float(request.form.get('credit', '').strip())
        course.hours = int(request.form.get('hours', '').strip())
        course.teacher_id = request.form.get('teacher_id', '').strip() or None
        course.semester = request.form.get('semester', '').strip()
        course.capacity = int(request.form.get('capacity', 60))
        
        try:
            db.session.commit()
            flash('课程信息更新成功', 'success')
            return redirect(url_for('admin_bp.course_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('admin/course_form.html', course=course, teachers=teachers)

@admin_bp.route('/courses/delete/<string:course_id>')
@admin_required
def course_delete(course_id):
    """删除课程"""
    course = Course.query.get_or_404(course_id)
    
    try:
        # 级联删除：会同时删除对应的选课和成绩
        db.session.delete(course)
        db.session.commit()
        flash('课程删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.course_list'))

# ==============================
# 排课管理
# ==============================
@admin_bp.route('/schedules')
@admin_required
def schedule_list():
    """排课列表"""
    schedules = Schedule.query.all()
    return render_template('admin/schedule_list.html', schedules=schedules)

@admin_bp.route('/schedules/add', methods=['GET', 'POST'])
@admin_required
def schedule_add():
    """添加排课"""
    courses = Course.query.all()
    
    if request.method == 'POST':
        course_id = request.form.get('course_id', '').strip()
        day_of_week = request.form.get('day_of_week', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        classroom = request.form.get('classroom', '').strip()
        
        # 表单验证
        if not course_id or not day_of_week or not start_time or not end_time or not classroom:
            flash('所有字段不能为空', 'danger')
            return render_template('admin/schedule_form.html', courses=courses)
        
        try:
            day_of_week = int(day_of_week)
            if day_of_week < 1 or day_of_week > 7:
                raise ValueError
        except ValueError:
            flash('星期必须是1-7之间的数字', 'danger')
            return render_template('admin/schedule_form.html', courses=courses)
        
        # 冲突检查
        course = Course.query.get(course_id)
        conflict = check_schedule_conflict(course_id, day_of_week, start_time, end_time, classroom, course.teacher_id)
        if conflict:
            flash(conflict, 'danger')
            return render_template('admin/schedule_form.html', courses=courses)
        
        try:
            schedule = Schedule(
                course_id=course_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                classroom=classroom
            )
            db.session.add(schedule)
            db.session.commit()
            
            flash('排课添加成功', 'success')
            return redirect(url_for('admin_bp.schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('admin/schedule_form.html', courses=courses)

@admin_bp.route('/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
@admin_required
def schedule_edit(schedule_id):
    """编辑排课"""
    schedule = Schedule.query.get_or_404(schedule_id)
    courses = Course.query.all()
    
    if request.method == 'POST':
        course_id = request.form.get('course_id', '').strip()
        day_of_week = request.form.get('day_of_week', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        classroom = request.form.get('classroom', '').strip()
        
        # 表单验证
        if not course_id or not day_of_week or not start_time or not end_time or not classroom:
            flash('所有字段不能为空', 'danger')
            return render_template('admin/schedule_form.html', schedule=schedule, courses=courses)
        
        try:
            day_of_week = int(day_of_week)
            if day_of_week < 1 or day_of_week > 7:
                raise ValueError
        except ValueError:
            flash('星期必须是1-7之间的数字', 'danger')
            return render_template('admin/schedule_form.html', schedule=schedule, courses=courses)
        
        # 冲突检查（排除当前排课）
        course = Course.query.get(course_id)
        conflict = check_schedule_conflict(
            course_id, day_of_week, start_time, end_time, classroom, course.teacher_id, exclude_id=schedule_id
        )
        if conflict:
            flash(conflict, 'danger')
            return render_template('admin/schedule_form.html', schedule=schedule, courses=courses)
        
        try:
            schedule.course_id = course_id
            schedule.day_of_week = day_of_week
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.classroom = classroom
            db.session.commit()
            
            flash('排课更新成功', 'success')
            return redirect(url_for('admin_bp.schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('admin/schedule_form.html', schedule=schedule, courses=courses)

@admin_bp.route('/schedules/delete/<int:schedule_id>')
@admin_required
def schedule_delete(schedule_id):
    """删除排课"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        flash('排课删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.schedule_list'))

# ==============================
# 排课冲突检查工具函数
# ==============================
def check_schedule_conflict(course_id, day_of_week, start_time, end_time, classroom, teacher_id, exclude_id=None):
    """
    检查排课冲突
    返回冲突信息，无冲突返回None
    """
    # 1. 检查同一教室同一时间是否有其他课程
    classroom_conflict = Schedule.query.filter(
        Schedule.classroom == classroom,
        Schedule.day_of_week == day_of_week,
        Schedule.start_time == start_time,
        Schedule.end_time == end_time
    )
    if exclude_id:
        classroom_conflict = classroom_conflict.filter(Schedule.id != exclude_id)
    
    if classroom_conflict.first():
        return f"教室 {classroom} 在周{day_of_week} {start_time}-{end_time} 已有课程安排"
    
    # 2. 检查同一教师同一时间是否有其他课程
    if teacher_id:
        teacher_conflict = Schedule.query.join(
            Course, Course.course_id == Schedule.course_id
        ).filter(
            Course.teacher_id == teacher_id,
            Schedule.day_of_week == day_of_week,
            Schedule.start_time == start_time,
            Schedule.end_time == end_time
        )
        if exclude_id:
            teacher_conflict = teacher_conflict.filter(Schedule.id != exclude_id)
        
        if teacher_conflict.first():
            return f"该教师在周{day_of_week} {start_time}-{end_time} 已有其他课程安排"
    
    return None
