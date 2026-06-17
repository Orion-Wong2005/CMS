from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.extensions import db
from app.models import Student, Course, Enrollment, Grade, Schedule
from app.utils.decorators import student_required

student_bp = Blueprint('student_bp', __name__, url_prefix='/student')

# ==============================
# 工具函数：计算绩点
# ==============================
def calculate_gpa(grade):
    """根据百分制成绩计算4.0制绩点"""
    if grade is None:
        return None
    if grade >= 90:
        return 4.0
    elif grade >= 85:
        return 3.7
    elif grade >= 82:
        return 3.3
    elif grade >= 78:
        return 3.0
    elif grade >= 75:
        return 2.7
    elif grade >= 72:
        return 2.3
    elif grade >= 68:
        return 2.0
    elif grade >= 64:
        return 1.5
    elif grade >= 60:
        return 1.0
    else:
        return 0.0

# ==============================
# 学生首页
# ==============================
@student_bp.route('/')
@student_required
def index():
    """学生首页 - 个人信息与学习概览"""
    # 获取当前登录学生信息
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 统计数据
    enrolled_count = Enrollment.query.filter_by(
        student_id=student.student_id, 
        status=1
    ).count()
    
    total_credit = db.session.query(db.func.sum(Course.credit)).join(
        Enrollment, Enrollment.course_id == Course.course_id
    ).filter(
        Enrollment.student_id == student.student_id,
        Enrollment.status == 1
    ).scalar() or 0
    
    # 已出成绩的课程数
    graded_count = Grade.query.filter_by(student_id=student.student_id).count()
    
    return render_template('student/index.html',
                          student=student,
                          enrolled_count=enrolled_count,
                          total_credit=round(total_credit, 1),
                          graded_count=graded_count)

# ==============================
# 可选课程列表（选课中心）
# ==============================
@student_bp.route('/courses')
@student_required
def course_list():
    """显示所有可选课程，带选课状态和容量信息"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 获取所有课程
    courses = Course.query.all()
    
    # 为每个课程添加额外信息：已选人数、是否已选
    course_info_list = []
    for course in courses:
        # 计算已选人数（只统计正常选课状态）
        enrolled_num = Enrollment.query.filter_by(
            course_id=course.course_id, 
            status=1
        ).count()
        
        # 检查当前学生是否已选该课程
        is_enrolled = Enrollment.query.filter_by(
            student_id=student.student_id,
            course_id=course.course_id,
            status=1
        ).first() is not None
        
        course_info_list.append({
            'course': course,
            'enrolled_num': enrolled_num,
            'is_enrolled': is_enrolled,
            'is_full': enrolled_num >= course.capacity
        })
    
    return render_template('student/course_list.html',
                          course_info_list=course_info_list)

# ==============================
# 选课核心功能
# ==============================
@student_bp.route('/enroll/<string:course_id>')
@student_required
def enroll(course_id):
    """学生选课"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    course = Course.query.get_or_404(course_id)
    
    # 1. 检查是否已选该课程
    existing_enrollment = Enrollment.query.filter_by(
        student_id=student.student_id,
        course_id=course_id,
        status=1
    ).first()
    
    if existing_enrollment:
        flash('您已选过该课程，无需重复选课', 'warning')
        return redirect(url_for('student_bp.course_list'))
    
    # 2. 检查课程容量
    enrolled_num = Enrollment.query.filter_by(
        course_id=course_id, 
        status=1
    ).count()
    
    if enrolled_num >= course.capacity:
        flash('课程容量已满，选课失败', 'danger')
        return redirect(url_for('student_bp.course_list'))
    
    try:
        # 3. 创建选课记录
        enrollment = Enrollment(
            student_id=student.student_id,
            course_id=course_id
        )
        db.session.add(enrollment)
        
        # 4. 预创建成绩记录（方便教师后续录入）
        grade = Grade(
            student_id=student.student_id,
            course_id=course_id,
            grade=None
        )
        db.session.add(grade)
        
        db.session.commit()
        flash(f'选课成功！您已成功选修《{course.course_name}》', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'选课失败：{str(e)}', 'danger')
    
    return redirect(url_for('student_bp.course_list'))

# ==============================
# 退课核心功能
# ==============================
@student_bp.route('/drop/<int:enrollment_id>')
@student_required
def drop(enrollment_id):
    """学生退课（软删除，保留历史记录）"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 检查选课记录是否存在且属于当前学生
    enrollment = Enrollment.query.filter_by(
        id=enrollment_id,
        student_id=student.student_id,
        status=1
    ).first()
    
    if not enrollment:
        flash('选课记录不存在或已退课', 'danger')
        return redirect(url_for('student_bp.my_courses'))
    
    course = Course.query.get(enrollment.course_id)
    
    try:
        # 1. 软删除选课记录（修改状态为0）
        enrollment.status = 0
        
        # 2. 删除对应的成绩记录
        Grade.query.filter_by(
            student_id=student.student_id,
            course_id=enrollment.course_id
        ).delete()
        
        db.session.commit()
        flash(f'退课成功！您已退选《{course.course_name}》', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'退课失败：{str(e)}', 'danger')
    
    return redirect(url_for('student_bp.my_courses'))

# ==============================
# 我的课程（已选课程）
# ==============================
@student_bp.route('/my-courses')
@student_required
def my_courses():
    """查看已选课程"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询所有正常选课状态的课程
    enrollments = Enrollment.query.filter_by(
        student_id=student.student_id,
        status=1
    ).all()
    
    # 为每个选课记录添加课程信息和成绩
    course_list = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        grade = Grade.query.filter_by(
            student_id=student.student_id,
            course_id=course.course_id
        ).first()
        
        course_list.append({
            'enrollment_id': enrollment.id,
            'course': course,
            'enroll_time': enrollment.enroll_time,
            'grade': grade.grade if grade else None,
            'gpa': calculate_gpa(grade.grade) if grade and grade.grade else None
        })
    
    return render_template('student/my_courses.html',
                          course_list=course_list)

# ==============================
# 我的成绩查询
# ==============================
@student_bp.route('/grades')
@student_required
def grades():
    """查看所有已出成绩"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询所有有成绩的记录
    grades = Grade.query.filter(
        Grade.student_id == student.student_id,
        Grade.grade.isnot(None)
    ).all()
    
    # 为每个成绩添加课程信息和绩点
    grade_list = []
    total_credit = 0
    total_grade_point = 0
    
    for grade in grades:
        course = Course.query.get(grade.course_id)
        gpa = calculate_gpa(grade.grade)
        
        grade_list.append({
            'course': course,
            'grade': grade.grade,
            'gpa': gpa,
            'credit': course.credit,
            'remark': grade.remark
        })
        
        # 计算加权平均绩点
        if gpa is not None:
            total_credit += course.credit
            total_grade_point += gpa * course.credit
    
    # 计算平均绩点
    gpa_avg = round(total_grade_point / total_credit, 2) if total_credit > 0 else 0
    
    return render_template('student/my_grades.html',
                          grade_list=grade_list,
                          total_credit=total_credit,
                          gpa_avg=gpa_avg)

# ==============================
# 个人信息修改
# ==============================
@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    """修改个人信息"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        # 只允许修改联系方式，不允许修改学号、姓名等关键信息
        student.phone = request.form.get('phone', '').strip()
        student.email = request.form.get('email', '').strip()
        
        try:
            db.session.commit()
            flash('个人信息修改成功', 'success')
            return redirect(url_for('student_bp.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'修改失败：{str(e)}', 'danger')
    
    return render_template('student/profile.html', student=student)

# ==============================
# 我的课表
# ==============================
@student_bp.route('/schedule')
@student_required
def my_schedule():
    """查看个人课表"""
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询学生所有已选课程的排课
    enrollments = Enrollment.query.filter_by(
        student_id=student.student_id,
        status=1
    ).all()
    
    # 初始化课表表格（7天 x 12节）
    schedule_table = [[None for _ in range(8)] for _ in range(13)]  # 行：节次1-12，列：星期1-7
    
    for enrollment in enrollments:
        course = enrollment.course
        schedules = Schedule.query.filter_by(course_id=course.course_id).all()
        
        for schedule in schedules:
            day = schedule.day_of_week
            start = int(schedule.start_time)
            end = int(schedule.end_time)
            
            # 将课程信息填入课表
            for period in range(start, end + 1):
                schedule_table[period][day] = {
                    'course_name': course.course_name,
                    'teacher': course.teacher.name if course.teacher else '未分配',
                    'classroom': schedule.classroom,
                    'rowspan': end - start + 1,
                    'is_first': (period == start)
                }
    
    return render_template('student/my_schedule.html',
                          schedule_table=schedule_table,
                          days=['周一', '周二', '周三', '周四', '周五', '周六', '周日'])

# ==============================
# 获取课表数据（用于前端导出）
# ==============================
@student_bp.route('/schedule/export/data')
@student_required
def schedule_export_data():
    """获取课表数据（JSON格式，用于前端导出）"""
    from flask import jsonify
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询学生所有已选课程的排课
    enrollments = Enrollment.query.filter_by(
        student_id=student.student_id,
        status=1
    ).all()
    
    # 构建课表矩阵（12节 x 7天）
    schedule_matrix = [['' for _ in range(7)] for _ in range(12)]
    
    for enrollment in enrollments:
        course = enrollment.course
        schedules = Schedule.query.filter_by(course_id=course.course_id).all()
        
        for schedule in schedules:
            day_idx = int(schedule.day_of_week) - 1  # 转换为0-6索引
            start_period = int(schedule.start_time) - 1  # 转换为0-11索引
            end_period = int(schedule.end_time) - 1
            
            # 在所有节次中填充课程信息
            for period in range(start_period, end_period + 1):
                if period < 12 and day_idx < 7:
                    teacher_name = course.teacher.name if course.teacher else '未分配'
                    schedule_matrix[period][day_idx] = f"{course.course_name}\n{teacher_name} - {schedule.classroom}"
    
    # 转换为行格式
    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    rows = []
    
    for period in range(12):
        row = [f'第{period + 1}节']
        for day in range(7):
            row.append(schedule_matrix[period][day])
        rows.append(row)
    
    return jsonify({
        'filename': f'课表_{student.student_id}.csv',
        'headers': ['节次', '周一', '周二', '周三', '周四', '周五', '周六', '周日'],
        'rows': rows
    })

# ==============================
# 导出课表为CSV（直接下载）
# ==============================
@student_bp.route('/schedule/export')
@student_required
def export_schedule():
    """导出课表为CSV文件（浏览器下载）"""
    import csv
    from io import StringIO
    from flask import make_response
    from urllib.parse import quote
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询学生所有已选课程的排课
    enrollments = Enrollment.query.filter_by(
        student_id=student.student_id,
        status=1
    ).all()
    
    # 获取所有排课信息
    schedule_data = []
    
    for enrollment in enrollments:
        course = enrollment.course
        schedules = Schedule.query.filter_by(course_id=course.course_id).all()
        
        for schedule in schedules:
            schedule_data.append({
                'course_name': course.course_name,
                'teacher': course.teacher.name if course.teacher else '未分配',
                'classroom': schedule.classroom,
                'day_of_week': ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'][schedule.day_of_week],
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'credit': course.credit
            })
    
    # 使用StringIO生成CSV内容（支持中文）
    output = StringIO()
    
    # 创建CSV写入器
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['课程名称', '教师', '教室', '星期', '开始节次', '结束节次', '学分'])
    
    # 写入数据
    for item in schedule_data:
        writer.writerow([
            item['course_name'],
            item['teacher'],
            item['classroom'],
            item['day_of_week'],
            item['start_time'],
            item['end_time'],
            item['credit']
        ])
    
    # 获取CSV内容（添加BOM以支持Excel中文显示）
    csv_content = '\ufeff' + output.getvalue()
    
    # 生成文件名（支持中文）
    filename = f'课表_{student.student_id}.csv'
    encoded_filename = quote(filename, encoding='utf-8')
    
    # 设置Content-Disposition头（同时支持filename和filename*）
    content_disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
    
    # 创建响应
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = content_disposition
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# ==============================
# 获取成绩数据（用于前端导出）
# ==============================
@student_bp.route('/grades/export/data')
@student_required
def grades_export_data():
    """获取成绩数据（JSON格式，用于前端导出）"""
    from flask import jsonify
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询所有有成绩的记录
    grades = Grade.query.filter(
        Grade.student_id == student.student_id,
        Grade.grade.isnot(None)
    ).all()
    
    # 计算成绩信息
    rows = []
    total_credit = 0
    total_grade_point = 0
    
    for grade in grades:
        course = Course.query.get(grade.course_id)
        gpa = calculate_gpa(grade.grade)
        
        rows.append([
            course.course_id,
            course.course_name,
            course.credit,
            grade.grade,
            gpa,
            grade.remark or ''
        ])
        
        if gpa is not None:
            total_credit += course.credit
            total_grade_point += gpa * course.credit
    
    gpa_avg = round(total_grade_point / total_credit, 2) if total_credit > 0 else 0
    
    return jsonify({
        'filename': f'学分绩_{student.student_id}.csv',
        'header_info': [
            ['学号', student.student_id],
            ['姓名', student.name],
            ['平均绩点', gpa_avg]
        ],
        'headers': ['课程编号', '课程名称', '学分', '成绩', '绩点', '备注'],
        'rows': rows
    })

# ==============================
# 导出学分绩为CSV（直接下载）
# ==============================
@student_bp.route('/grades/export')
@student_required
def export_grades():
    """导出学分绩为CSV文件（浏览器下载）"""
    import csv
    from io import StringIO
    from flask import make_response
    from urllib.parse import quote
    
    student = Student.query.filter_by(user_id=session['user_id']).first()
    
    # 查询所有有成绩的记录
    grades = Grade.query.filter(
        Grade.student_id == student.student_id,
        Grade.grade.isnot(None)
    ).all()
    
    # 计算成绩信息
    grade_data = []
    total_credit = 0
    total_grade_point = 0
    
    for grade in grades:
        course = Course.query.get(grade.course_id)
        gpa = calculate_gpa(grade.grade)
        
        grade_data.append({
            'course_name': course.course_name,
            'course_id': course.course_id,
            'credit': course.credit,
            'grade': grade.grade,
            'gpa': gpa,
            'remark': grade.remark or ''
        })
        
        if gpa is not None:
            total_credit += course.credit
            total_grade_point += gpa * course.credit
    
    gpa_avg = round(total_grade_point / total_credit, 2) if total_credit > 0 else 0
    
    # 使用StringIO生成CSV内容（支持中文）
    output = StringIO()
    
    # 创建CSV写入器
    writer = csv.writer(output)
    
    # 写入头部信息
    writer.writerow(['学号', student.student_id])
    writer.writerow(['姓名', student.name])
    writer.writerow(['平均绩点', gpa_avg])
    writer.writerow([])
    writer.writerow(['课程编号', '课程名称', '学分', '成绩', '绩点', '备注'])
    
    # 写入成绩数据
    for item in grade_data:
        writer.writerow([
            item['course_id'],
            item['course_name'],
            item['credit'],
            item['grade'],
            item['gpa'],
            item['remark']
        ])
    
    # 获取CSV内容（添加BOM以支持Excel中文显示）
    csv_content = '\ufeff' + output.getvalue()
    
    # 生成文件名（支持中文）
    filename = f'学分绩_{student.student_id}.csv'
    encoded_filename = quote(filename, encoding='utf-8')
    
    # 设置Content-Disposition头（同时支持filename和filename*）
    content_disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
    
    # 创建响应
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = content_disposition
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
