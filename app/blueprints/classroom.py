# app/blueprints/classroom.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app.extensions import db
from app.models import Classroom, ClassroomSchedule, Course
from app.utils.decorators import admin_required, login_required
from sqlalchemy import and_
from sqlalchemy import text

classroom_bp = Blueprint('classroom', __name__, url_prefix='/classroom')


# ==================== 教室管理 ====================
@classroom_bp.route('/admin/manage')
@login_required
@admin_required
def admin_manage():
    """教室管理页面"""
    return render_template('classroom/admin_manage.html')


@classroom_bp.route('/api/classrooms', methods=['GET'])
@login_required
def get_classrooms():
    """获取教室列表"""
    building = request.args.get('building', '')
    type_filter = request.args.get('type', '')
    status = request.args.get('status', '')

    query = Classroom.query
    if building:
        query = query.filter(Classroom.building.like(f'%{building}%'))
    if type_filter:
        query = query.filter(Classroom.type == type_filter)
    if status:
        query = query.filter(Classroom.status == status)

    classrooms = query.all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in classrooms]})


@classroom_bp.route('/api/classrooms', methods=['POST'])
@login_required
@admin_required
def add_classroom():
    """添加教室"""
    data = request.get_json()

    # 检查教室编号是否已存在
    existing = Classroom.query.filter_by(classroom_number=data.get('classroom_number')).first()
    if existing:
        return jsonify({'code': 400, 'message': '教室编号已存在'})

    classroom = Classroom(
        classroom_number=data.get('classroom_number'),
        building=data.get('building'),
        floor=data.get('floor'),
        capacity=data.get('capacity', 60),
        type=data.get('type', '普通教室'),
        equipment=data.get('equipment', ''),
        status=data.get('status', '可用')
    )

    db.session.add(classroom)
    db.session.commit()

    return jsonify({'code': 200, 'message': '添加成功', 'data': classroom.to_dict()})


@classroom_bp.route('/api/classrooms/<int:classroom_id>', methods=['PUT'])
@login_required
@admin_required
def update_classroom(classroom_id):
    """更新教室信息"""
    classroom = Classroom.query.get_or_404(classroom_id)
    data = request.get_json()

    # 检查教室编号是否冲突
    if 'classroom_number' in data and data['classroom_number'] != classroom.classroom_number:
        existing = Classroom.query.filter_by(classroom_number=data['classroom_number']).first()
        if existing:
            return jsonify({'code': 400, 'message': '教室编号已存在'})
        classroom.classroom_number = data['classroom_number']

    if 'building' in data:
        classroom.building = data['building']
    if 'floor' in data:
        classroom.floor = data['floor']
    if 'capacity' in data:
        classroom.capacity = data['capacity']
    if 'type' in data:
        classroom.type = data['type']
    if 'equipment' in data:
        classroom.equipment = data['equipment']
    if 'status' in data:
        classroom.status = data['status']

    db.session.commit()

    return jsonify({'code': 200, 'message': '更新成功', 'data': classroom.to_dict()})


@classroom_bp.route('/api/classrooms/<int:classroom_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_classroom(classroom_id):
    """删除教室"""
    classroom = Classroom.query.get_or_404(classroom_id)

    # 检查是否有排课记录
    schedule_count = ClassroomSchedule.query.filter_by(classroom_id=classroom_id).count()
    if schedule_count > 0:
        return jsonify({'code': 400, 'message': f'该教室有{schedule_count}条排课记录，无法删除'})

    db.session.delete(classroom)
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})


# ==================== 教室排课管理 ====================
@classroom_bp.route('/admin/schedules')
@login_required
@admin_required
def admin_schedules():
    """教室排课管理页面"""
    classrooms = Classroom.query.filter_by(status='可用').all()
    courses = Course.query.all()
    return render_template('classroom/schedule_manage.html', classrooms=classrooms, courses=courses)


@classroom_bp.route('/api/schedules', methods=['GET'])
@login_required
def get_schedules():
    """获取排课列表"""
    classroom_id = request.args.get('classroom_id', type=int)
    semester = request.args.get('semester', '')
    week = request.args.get('week', type=int)
    weekday = request.args.get('weekday', type=int)

    query = ClassroomSchedule.query
    if classroom_id:
        query = query.filter_by(classroom_id=classroom_id)
    if semester:
        query = query.filter_by(semester=semester)
    if week:
        query = query.filter_by(week=week)
    if weekday:
        query = query.filter_by(weekday=weekday)

    schedules = query.all()
    return jsonify({'code': 200, 'data': [s.to_dict() for s in schedules]})


@classroom_bp.route('/api/schedules', methods=['POST'])
@login_required
@admin_required
def add_schedule():
    """添加教室排课 - 带冲突检测"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '请求数据为空'})
        
        # 参数验证
        required_fields = ['classroom_id', 'course_id', 'semester', 'week', 'weekday', 'start_section', 'end_section']
        for field in required_fields:
            if field not in data:
                return jsonify({'code': 400, 'message': f'缺少参数: {field}'})
        
        # 类型转换
        try:
            classroom_id = int(data['classroom_id'])
            course_id = data['course_id']
            semester = str(data['semester'])
            week = int(data['week'])
            weekday = int(data['weekday'])
            start_section = int(data['start_section'])
            end_section = int(data['end_section'])
        except ValueError as e:
            return jsonify({'code': 400, 'message': f'参数格式错误: {str(e)}'})
        
        # 验证节次范围
        if start_section < 1 or start_section > 12:
            return jsonify({'code': 400, 'message': '开始节次必须在1-12之间'})
        if end_section < 1 or end_section > 12:
            return jsonify({'code': 400, 'message': '结束节次必须在1-12之间'})
        if start_section > end_section:
            return jsonify({'code': 400, 'message': '开始节次不能大于结束节次'})
        
        # 验证周次
        if week < 1 or week > 20:
            return jsonify({'code': 400, 'message': '周次必须在1-20之间'})
        
        # 验证星期
        if weekday < 1 or weekday > 7:
            return jsonify({'code': 400, 'message': '星期必须在1-7之间'})
        
        # 检查教室是否存在
        classroom = Classroom.query.get(classroom_id)
        if not classroom:
            return jsonify({'code': 400, 'message': '教室不存在'})
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'code': 400, 'message': '课程不存在'})
        
        # 检查时间冲突
        conflict = check_time_conflict(
            classroom_id=classroom_id,
            semester=semester,
            week=week,
            weekday=weekday,
            start_section=start_section,
            end_section=end_section,
            exclude_id=None
        )
        
        if conflict:
            return jsonify({
                'code': 400,
                'message': f'时间冲突！该时间段已有课程：{conflict.course.course_name}'
            })
        
        # 创建排课记录
        schedule = ClassroomSchedule(
            classroom_id=classroom_id,
            course_id=course_id,
            semester=semester,
            week=week,
            weekday=weekday,
            start_section=start_section,
            end_section=end_section
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '添加成功', 'data': schedule.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        print(f"添加排课错误: {str(e)}")  # 打印到控制台便于调试
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'})


@classroom_bp.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
@login_required
@admin_required
def update_schedule(schedule_id):
    """更新教室排课"""
    schedule = ClassroomSchedule.query.get_or_404(schedule_id)
    data = request.get_json()

    # 检查冲突
    conflict = check_time_conflict(
        classroom_id=data.get('classroom_id', schedule.classroom_id),
        semester=data.get('semester', schedule.semester),
        week=data.get('week', schedule.week),
        weekday=data.get('weekday', schedule.weekday),
        start_section=data.get('start_section', schedule.start_section),
        end_section=data.get('end_section', schedule.end_section),
        exclude_id=schedule_id
    )

    if conflict:
        return jsonify({
            'code': 400,
            'message': f'时间冲突！该时间段已有课程：{conflict.course.course_name}'
        })

    if 'classroom_id' in data:
        schedule.classroom_id = data['classroom_id']
    if 'course_id' in data:
        schedule.course_id = data['course_id']
    if 'semester' in data:
        schedule.semester = data['semester']
    if 'week' in data:
        schedule.week = data['week']
    if 'weekday' in data:
        schedule.weekday = data['weekday']
    if 'start_section' in data:
        schedule.start_section = data['start_section']
    if 'end_section' in data:
        schedule.end_section = data['end_section']

    db.session.commit()

    return jsonify({'code': 200, 'message': '更新成功'})


@classroom_bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_schedule(schedule_id):
    """删除教室排课"""
    schedule = ClassroomSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})


def check_time_conflict(classroom_id, semester, week, weekday, start_section, end_section, exclude_id=None):
    """检查时间冲突 - 同一教室同一时间段不能安排多门课"""
    try:
        query = ClassroomSchedule.query.filter(
            and_(
                ClassroomSchedule.classroom_id == classroom_id,
                ClassroomSchedule.semester == semester,
                ClassroomSchedule.week == week,
                ClassroomSchedule.weekday == weekday,
                ClassroomSchedule.start_section < end_section,
                ClassroomSchedule.end_section > start_section
            )
        )
        
        if exclude_id:
            query = query.filter(ClassroomSchedule.id != exclude_id)
        
        return query.first()
    except Exception as e:
        print(f"冲突检查错误: {str(e)}")
        return None

# ==================== 教室课表查询 ====================
@classroom_bp.route('/schedule_query')
@login_required
def schedule_query():
    """教室课表查询页面"""
    classrooms = Classroom.query.filter_by(status='可用').all()
    return render_template('classroom/schedule_query.html', classrooms=classrooms)


@classroom_bp.route('/api/classroom_timetable')
@login_required
def get_classroom_timetable():
    """获取教室课表"""
    classroom_id = request.args.get('classroom_id', type=int)
    semester = request.args.get('semester', '')
    week = request.args.get('week', type=int)

    if not classroom_id:
        return jsonify({'code': 400, 'message': '请选择教室'})

    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return jsonify({'code': 400, 'message': '教室不存在'})

    # 构建查询条件
    query = ClassroomSchedule.query.filter_by(classroom_id=classroom_id)

    if semester:
        query = query.filter_by(semester=semester)
    if week:
        query = query.filter_by(week=week)

    schedules = query.order_by(ClassroomSchedule.weekday, ClassroomSchedule.start_section).all()

    # 构建课表矩阵 (节次1-12, 星期1-7)
    matrix = []
    for section in range(1, 13):
        row = {'section': section, 'display': f'第{section}节'}
        for weekday_num in range(1, 8):
            row[f'weekday_{weekday_num}'] = None
        matrix.append(row)

    for schedule in schedules:
        for section in range(schedule.start_section, schedule.end_section + 1):
            if 1 <= section <= 12:
                idx = section - 1
                matrix[idx][f'weekday_{schedule.weekday}'] = {
                    'course_name': schedule.course.course_name,
                    'course_id': schedule.course_id,
                    'schedule_id': schedule.id,
                    'teacher': schedule.course.teacher.name if schedule.course.teacher else ''
                }

    return jsonify({
        'code': 200,
        'data': {
            'classroom': classroom.to_dict(),
            'timetable': matrix,
            'schedules': [s.to_dict() for s in schedules]
        }
    })


# ==================== 教室使用统计（CTE递归查询） ====================
@classroom_bp.route('/admin/usage_stats')
@login_required
@admin_required
def usage_stats():
    """教室使用统计页面"""
    return render_template('classroom/usage_stats.html')


@classroom_bp.route('/api/classroom_usage_stats')
@login_required
@admin_required
def get_classroom_usage_stats():
    """
    使用CTE递归统计各教室在学期中的使用次数
    通过生成学期所有周次，然后与排课表关联统计
    """
    try:
        semester = request.args.get('semester', '')
        
        if not semester:
            # 获取最新的学期
            latest_schedule = ClassroomSchedule.query.order_by(ClassroomSchedule.semester.desc()).first()
            if latest_schedule:
                semester = latest_schedule.semester
            else:
                return jsonify({'code': 400, 'message': '暂无数据，请先创建排课'})
        
        # SQLite 兼容的 CTE 递归查询，使用 text() 包裹
        sql = text("""
            WITH RECURSIVE weeks(week_num) AS (
                SELECT 1
                UNION ALL
                SELECT week_num + 1 FROM weeks WHERE week_num < 20
            ),
            classroom_usage AS (
                SELECT 
                    c.id as classroom_id,
                    c.classroom_number,
                    c.building,
                    c.type,
                    c.capacity,
                    w.week_num,
                    COUNT(cs.id) as weekly_usage
                FROM classrooms c
                CROSS JOIN weeks w
                LEFT JOIN classroom_schedules cs ON 
                    cs.classroom_id = c.id 
                    AND cs.semester = :semester
                    AND cs.week = w.week_num
                GROUP BY c.id, c.classroom_number, c.building, c.type, c.capacity, w.week_num
            )
            SELECT 
                classroom_id,
                classroom_number,
                building,
                type,
                capacity,
                COALESCE(SUM(weekly_usage), 0) as total_usage,
                COALESCE(ROUND(AVG(weekly_usage), 2), 0) as avg_weekly_usage,
                COALESCE(MAX(weekly_usage), 0) as max_weekly_usage,
                COALESCE(MIN(weekly_usage), 0) as min_weekly_usage,
                COUNT(CASE WHEN weekly_usage > 0 THEN 1 END) as used_weeks
            FROM classroom_usage
            GROUP BY classroom_id, classroom_number, building, type, capacity
            ORDER BY total_usage DESC
        """)
        
        from app.extensions import db
        result = db.session.execute(sql, {'semester': semester})
        rows = result.fetchall()
        
        stats = []
        for row in rows:
            stats.append({
                'classroom_id': row[0],
                'classroom_number': row[1],
                'building': row[2],
                'type': row[3],
                'capacity': row[4],
                'total_usage': int(row[5]),
                'avg_weekly_usage': float(row[6]),
                'max_weekly_usage': int(row[7]),
                'min_weekly_usage': int(row[8]),
                'used_weeks': int(row[9])
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'semester': semester,
                'stats': stats
            }
        })
    
    except Exception as e:
        print(f"统计错误: {str(e)}")
        return jsonify({'code': 500, 'message': f'统计失败: {str(e)}'})


# ==================== 获取筛选选项 ====================
@classroom_bp.route('/api/filter_options')
@login_required
def get_filter_options():
    """获取筛选选项"""
    buildings = db.session.query(Classroom.building).distinct().all()
    types = db.session.query(Classroom.type).distinct().all()
    statuses = db.session.query(Classroom.status).distinct().all()

    return jsonify({
        'code': 200,
        'data': {
            'buildings': [b[0] for b in buildings if b[0]],
            'types': [t[0] for t in types if t[0]],
            'statuses': [s[0] for s in statuses if s[0]]
        }
    })