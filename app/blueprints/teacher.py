from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from io import BytesIO
from openpyxl import Workbook
from app.extensions import db
from app.models import Teacher, Course, Enrollment, Grade, Schedule
from app.utils.decorators import teacher_required
from app.utils.schedule_utils import PERIOD_TIMES, TOTAL_PERIODS, TOTAL_DAYS

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

# ==============================
# 教师首页
# ==============================
@teacher_bp.route('/')
@teacher_required
def index():
    """教师首页 - 教学概览"""
    # 获取当前登录教师信息
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    
    # 统计数据
    course_count = Course.query.filter_by(teacher_id=teacher.teacher_id).count()
    
    # 统计总学生数（去重）
    total_students = db.session.query(db.func.count(db.distinct(Enrollment.student_id))).join(
        Course, Course.course_id == Enrollment.course_id
    ).filter(
        Course.teacher_id == teacher.teacher_id,
        Enrollment.status == 1
    ).scalar() or 0
    
    # 待录入成绩的课程数
    pending_courses = 0
    courses = Course.query.filter_by(teacher_id=teacher.teacher_id).all()
    for course in courses:
        # 检查是否有学生成绩未录入
        ungraded_count = Grade.query.filter(
            Grade.course_id == course.course_id,
            Grade.grade.is_(None)
        ).count()
        if ungraded_count > 0:
            pending_courses += 1
    
    return render_template('teacher/index.html',
                          teacher=teacher,
                          course_count=course_count,
                          total_students=total_students,
                          pending_courses=pending_courses)

# ==============================
# 我的课程列表
# ==============================
@teacher_bp.route('/courses')
@teacher_required
def my_courses():
    """查看我教授的所有课程"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    courses = Course.query.filter_by(teacher_id=teacher.teacher_id).all()
    
    # 为每个课程添加学生人数和待录入成绩数
    course_info_list = []
    for course in courses:
        student_count = Enrollment.query.filter_by(
            course_id=course.course_id, 
            status=1
        ).count()
        
        ungraded_count = Grade.query.filter(
            Grade.course_id == course.course_id,
            Grade.grade.is_(None)
        ).count()
        
        course_info_list.append({
            'course': course,
            'student_count': student_count,
            'ungraded_count': ungraded_count
        })
    
    return render_template('teacher/my_courses.html',
                          course_info_list=course_info_list)

# ==============================
# 课程学生名单与成绩管理
# ==============================
@teacher_bp.route('/courses/<string:course_id>/students')
@teacher_required
def course_students(course_id):
    """查看某门课程的学生名单和成绩"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    
    # 权限校验：确保该课程属于当前教师
    course = Course.query.filter_by(
        course_id=course_id,
        teacher_id=teacher.teacher_id
    ).first_or_404()
    
    # 查询该课程的所有选课学生及成绩
    enrollments = Enrollment.query.filter_by(
        course_id=course_id,
        status=1
    ).all()
    
    student_list = []
    for enrollment in enrollments:
        student = enrollment.student
        grade = Grade.query.filter_by(
            student_id=student.student_id,
            course_id=course_id
        ).first()
        
        student_list.append({
            'student_id': student.student_id,
            'name': student.name,
            'major': student.major,
            'class_name': student.class_name,
            'grade': grade.grade if grade else None,
            'remark': grade.remark if grade else None
        })
    
    return render_template('teacher/course_students.html',
                          course=course,
                          student_list=student_list)

# ==============================
# 单个学生成绩录入/修改
# ==============================
@teacher_bp.route('/grades/edit/<string:course_id>/<string:student_id>', methods=['GET', 'POST'])
@teacher_required
def grade_edit(course_id, student_id):
    """录入或修改单个学生的成绩"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    
    # 权限校验
    course = Course.query.filter_by(
        course_id=course_id,
        teacher_id=teacher.teacher_id
    ).first_or_404()
    
    # 检查学生是否选修了该课程
    enrollment = Enrollment.query.filter_by(
        course_id=course_id,
        student_id=student_id,
        status=1
    ).first_or_404()
    
    student = enrollment.student
    grade = Grade.query.filter_by(
        course_id=course_id,
        student_id=student_id
    ).first()
    
    if request.method == 'POST':
        grade_value = request.form.get('grade', '').strip()
        remark = request.form.get('remark', '').strip()
        
        # 表单验证
        if not grade_value:
            flash('成绩不能为空', 'danger')
            return render_template('teacher/grade_form.html',
                                  course=course,
                                  student=student,
                                  grade=grade)
        
        try:
            grade_float = float(grade_value)
            if grade_float < 0 or grade_float > 100:
                flash('成绩必须在0-100之间', 'danger')
                return render_template('teacher/grade_form.html',
                                      course=course,
                                      student=student,
                                      grade=grade)
        except ValueError:
            flash('成绩必须是数字', 'danger')
            return render_template('teacher/grade_form.html',
                                  course=course,
                                  student=student,
                                  grade=grade)
        
        try:
            # 更新或创建成绩记录
            if grade:
                grade.grade = grade_float
                grade.remark = remark
            else:
                grade = Grade(
                    student_id=student_id,
                    course_id=course_id,
                    grade=grade_float,
                    remark=remark
                )
                db.session.add(grade)
            
            db.session.commit()
            flash('成绩保存成功', 'success')
            return redirect(url_for('teacher_bp.course_students', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'保存失败：{str(e)}', 'danger')
    
    return render_template('teacher/grade_form.html',
                          course=course,
                          student=student,
                          grade=grade)

# ==============================
# 批量成绩录入
# ==============================
@teacher_bp.route('/grades/batch/<string:course_id>', methods=['GET', 'POST'])
@teacher_required
def grade_batch(course_id):
    """批量录入课程所有学生的成绩"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    
    # 权限校验
    course = Course.query.filter_by(
        course_id=course_id,
        teacher_id=teacher.teacher_id
    ).first_or_404()
    
    # 查询该课程的所有选课学生及成绩
    enrollments = Enrollment.query.filter_by(
        course_id=course_id,
        status=1
    ).all()
    
    if request.method == 'POST':
        try:
            for enrollment in enrollments:
                student_id = enrollment.student_id
                grade_value = request.form.get(f'grade_{student_id}', '').strip()
                remark = request.form.get(f'remark_{student_id}', '').strip()
                
                if grade_value:
                    grade_float = float(grade_value)
                    if 0 <= grade_float <= 100:
                        grade = Grade.query.filter_by(
                            student_id=student_id,
                            course_id=course_id
                        ).first()
                        
                        if grade:
                            grade.grade = grade_float
                            grade.remark = remark
                        else:
                            grade = Grade(
                                student_id=student_id,
                                course_id=course_id,
                                grade=grade_float,
                                remark=remark
                            )
                            db.session.add(grade)
            
            db.session.commit()
            flash('批量成绩保存成功', 'success')
            return redirect(url_for('teacher_bp.course_students', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'批量保存失败：{str(e)}', 'danger')
    
    # 准备学生列表数据
    student_list = []
    for enrollment in enrollments:
        student = enrollment.student
        grade = Grade.query.filter_by(
            student_id=student.student_id,
            course_id=course_id
        ).first()
        
        student_list.append({
            'student_id': student.student_id,
            'name': student.name,
            'grade': grade.grade if grade else None,
            'remark': grade.remark if grade else None
        })
    
    return render_template('teacher/grade_batch.html',
                          course=course,
                          student_list=student_list)

# ==============================
# 成绩Excel导出
# ==============================
@teacher_bp.route('/grades/export/<string:course_id>')
@teacher_required
def grade_export(course_id):
    """导出课程成绩为Excel文件"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    
    # 权限校验
    course = Course.query.filter_by(
        course_id=course_id,
        teacher_id=teacher.teacher_id
    ).first_or_404()
    
    # 查询该课程的所有选课学生及成绩
    enrollments = Enrollment.query.filter_by(
        course_id=course_id,
        status=1
    ).all()
    
    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = f"{course.course_name}成绩表"
    
    # 设置表头
    headers = ['学号', '姓名', '专业', '班级', '成绩', '备注']
    ws.append(headers)
    
    # 填充数据
    for enrollment in enrollments:
        student = enrollment.student
        grade = Grade.query.filter_by(
            student_id=student.student_id,
            course_id=course_id
        ).first()
        
        row = [
            student.student_id,
            student.name,
            student.major,
            student.class_name,
            grade.grade if grade and grade.grade else '未录入',
            grade.remark if grade and grade.remark else ''
        ]
        ws.append(row)
    
    # 调整列宽
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column].width = adjusted_width
    
    # 保存到内存并返回
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={course.course_name}_成绩表.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

# ==============================
# 个人信息修改
# ==============================
@teacher_bp.route('/profile', methods=['GET', 'POST'])
@teacher_required
def profile():
    """修改个人信息"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        # 只允许修改联系方式，不允许修改工号、姓名等关键信息
        teacher.phone = request.form.get('phone', '').strip()
        teacher.email = request.form.get('email', '').strip()
        
        try:
            db.session.commit()
            flash('个人信息修改成功', 'success')
            return redirect(url_for('teacher_bp.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'修改失败：{str(e)}', 'danger')
    
    return render_template('teacher/profile.html', teacher=teacher)

# ==============================
# 我的课表
# ==============================
@teacher_bp.route('/schedule')
@teacher_required
def my_schedule():
    """查看个人课表"""
    teacher = Teacher.query.filter_by(user_id=session['user_id']).first()

    # 查询教师所有教授课程的排课
    courses = Course.query.filter_by(teacher_id=teacher.teacher_id).all()

    # 初始化课表表格（8节 x 7天）
    schedule_table = [[None for _ in range(TOTAL_DAYS + 1)] for _ in range(TOTAL_PERIODS + 1)]

    for course in courses:
        schedules = Schedule.query.filter_by(course_id=course.course_id).all()

        for sched in schedules:
            day = sched.day_of_week
            try:
                start = int(sched.start_time)
                end = int(sched.end_time)
            except (ValueError, TypeError):
                continue

            if start < 1 or end > TOTAL_PERIODS:
                continue

            for period in range(start, end + 1):
                schedule_table[period][day] = {
                    'course_name': course.course_name,
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

    return render_template('teacher/my_schedule.html',
                          schedule_table=schedule_table,
                          period_times=period_times,
                          days=['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
