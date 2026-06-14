from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from app.extensions import db
from app.models import Student, Course, Enrollment, Grade, Schedule
from app.utils.decorators import student_required
from app.utils.schedule_utils import (
    get_all_periods, get_period_time_range, format_schedule_time,
    format_schedule_summary, get_weekday_name, PERIOD_TIMES,
    TOTAL_PERIODS, TOTAL_DAYS
)

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
    
    # 为每个课程添加额外信息：已选人数、是否已选、上课时间
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

        # 获取课程的排课信息
        schedules = Schedule.query.filter_by(course_id=course.course_id).all()
        schedule_summaries = [format_schedule_summary(s) for s in schedules]

        course_info_list.append({
            'course': course,
            'enrolled_num': enrolled_num,
            'is_enrolled': is_enrolled,
            'is_full': enrolled_num >= course.capacity,
            'schedules': schedules,
            'schedule_summaries': schedule_summaries,
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
    
    # 1. 检查是否已选该课程（不分状态，先查是否有历史记录）
    existing_enrollment = Enrollment.query.filter_by(
        student_id=student.student_id,
        course_id=course_id
    ).first()

    if existing_enrollment and existing_enrollment.status == 1:
        flash('您已选过该课程，无需重复选课', 'warning')
        return redirect(url_for('student_bp.course_list'))

    # 2. 检查课程容量（退课后重新选课不算新占名额）
    if not existing_enrollment or existing_enrollment.status == 0:
        enrolled_num = Enrollment.query.filter_by(
            course_id=course_id,
            status=1
        ).count()

        if enrolled_num >= course.capacity:
            flash('课程容量已满，选课失败', 'danger')
            return redirect(url_for('student_bp.course_list'))

    try:
        if existing_enrollment and existing_enrollment.status == 0:
            # 3a. 退课后重新选课：恢复原记录
            existing_enrollment.status = 1
            existing_enrollment.enroll_time = datetime.now()
        else:
            # 3b. 首次选课：创建新记录
            enrollment = Enrollment(
                student_id=student.student_id,
                course_id=course_id
            )
            db.session.add(enrollment)

        # 4. 预创建成绩记录（如果已有则不重复创建）
        existing_grade = Grade.query.filter_by(
            student_id=student.student_id,
            course_id=course_id
        ).first()
        if not existing_grade:
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

    # 初始化课表表格（8节 x 7天）
    # schedule_table[period][day] period: 1-8, day: 1-7
    schedule_table = [[None for _ in range(TOTAL_DAYS + 1)] for _ in range(TOTAL_PERIODS + 1)]

    for enrollment in enrollments:
        course = enrollment.course
        schedules = Schedule.query.filter_by(course_id=course.course_id).all()

        for sched in schedules:
            day = sched.day_of_week
            try:
                start = int(sched.start_time)
                end = int(sched.end_time)
            except (ValueError, TypeError):
                continue

            # 只显示在 1-8 范围内的节次
            if start < 1 or end > TOTAL_PERIODS:
                continue

            # 将课程信息填入课表
            for period in range(start, end + 1):
                schedule_table[period][day] = {
                    'course_name': course.course_name,
                    'teacher': course.teacher.name if course.teacher else '未分配',
                    'classroom': sched.classroom,
                    'rowspan': end - start + 1,
                    'is_first': (period == start),
                    'semester': sched.semester,
                    'week_start': sched.week_start,
                    'week_end': sched.week_end,
                }

    # 构建节次与时间的映射列表
    period_times = [{'num': p, 'time': f"{PERIOD_TIMES[p]['start']}-{PERIOD_TIMES[p]['end']}"}
                    for p in range(1, TOTAL_PERIODS + 1)]

    return render_template('student/my_schedule.html',
                          schedule_table=schedule_table,
                          period_times=period_times,
                          days=['周一', '周二', '周三', '周四', '周五', '周六', '周日'])


# ==============================
# 教室课表查询（学生端）
# ==============================
@student_bp.route('/classroom-schedule')
@student_required
def classroom_schedule_query():
    """学生查询教室课表 - 查看每间教室该天每个时间段的课程"""
    from app.models import Classroom, ClassroomSchedule as CS

    classrooms = Classroom.query.filter_by(status='可用').order_by(Classroom.building, Classroom.classroom_number).all()
    return render_template('student/classroom_schedule.html', classrooms=classrooms,
                          periods=get_all_periods(), days=range(1, 8),
                          weekday_names=['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'])


@student_bp.route('/api/classroom-timetable')
@student_required
def api_classroom_timetable():
    """API: 获取指定教室的课表"""
    from app.models import Classroom, ClassroomSchedule as CS

    classroom_id = request.args.get('classroom_id', type=int)
    semester = request.args.get('semester', '')
    week = request.args.get('week', type=int)

    if not classroom_id:
        return jsonify({'code': 400, 'message': '请选择教室'})

    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return jsonify({'code': 400, 'message': '教室不存在'})

    # 查询该教室的所有排课
    schedules = Schedule.query.filter_by(classroom=classroom.classroom_number).all()

    # 也查询 ClassroomSchedule 模型的数据
    cs_query = CS.query.filter_by(classroom_id=classroom_id)
    if semester:
        cs_query = cs_query.filter_by(semester=semester)
    if week:
        cs_query = cs_query.filter_by(week=week)
    cs_schedules = cs_query.order_by(CS.weekday, CS.start_section).all()

    # 构建课表矩阵 (8节 x 7天)
    matrix = []
    for section in range(1, TOTAL_PERIODS + 1):
        time_info = PERIOD_TIMES[section]
        row = {
            'section': section,
            'time': f"{time_info['start']}-{time_info['end']}",
            'label': time_info['label']
        }
        for day_num in range(1, TOTAL_DAYS + 1):
            row[f'day_{day_num}'] = None
        matrix.append(row)

    # 填充 Schedule 模型数据
    for sched in schedules:
        try:
            start = int(sched.start_time)
            end = int(sched.end_time)
        except (ValueError, TypeError):
            continue
        if start < 1 or end > TOTAL_PERIODS:
            continue
        day = sched.day_of_week
        if day < 1 or day > TOTAL_DAYS:
            continue
        for section in range(start, end + 1):
            idx = section - 1
            matrix[idx][f'day_{day}'] = {
                'course_name': sched.course.course_name if sched.course else '',
                'course_id': sched.course_id,
                'teacher': sched.course.teacher.name if sched.course and sched.course.teacher else '',
                'classroom': sched.classroom,
                'period_range': f'{start}-{end}',
                'semester': sched.semester,
            }

    # 填充 ClassroomSchedule 模型数据（会覆盖同位置的 Schedule 数据）
    for cs in cs_schedules:
        for section in range(cs.start_section, cs.end_section + 1):
            if 1 <= section <= TOTAL_PERIODS:
                idx = section - 1
                matrix[idx][f'day_{cs.weekday}'] = {
                    'course_name': cs.course.course_name if cs.course else '',
                    'course_id': cs.course_id,
                    'teacher': cs.course.teacher.name if cs.course and cs.course.teacher else '',
                    'classroom': classroom.classroom_number,
                    'period_range': f'{cs.start_section}-{cs.end_section}',
                    'semester': cs.semester,
                }

    return jsonify({
        'code': 200,
        'data': {
            'classroom': classroom.to_dict(),
            'timetable': matrix,
        }
    })
