from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import Building, Classroom, Schedule, Course
from app.utils.decorators import admin_required

classroom_bp = Blueprint('classroom_bp', __name__, url_prefix='/classroom')

@classroom_bp.route('/buildings')
@admin_required
def building_list():
    buildings = Building.query.order_by(Building.building_code).all()
    return render_template('classroom/building_list.html', buildings=buildings)

@classroom_bp.route('/buildings/add', methods=['GET', 'POST'])
@admin_required
def building_add():
    if request.method == 'POST':
        building_code = request.form.get('building_code', '').strip()
        building_name = request.form.get('building_name', '').strip()
        campus = request.form.get('campus', '').strip()
        min_floor = request.form.get('min_floor', 1)
        max_floor = request.form.get('max_floor', 5)
        description = request.form.get('description', '').strip()
        
        if not building_code or not building_name:
            flash('楼栋编号和名称不能为空', 'danger')
            return render_template('classroom/building_form.html')
        
        if Building.query.filter_by(building_code=building_code).first():
            flash('该楼栋编号已存在', 'danger')
            return render_template('classroom/building_form.html')
        
        try:
            building = Building(
                building_code=building_code,
                building_name=building_name,
                campus=campus,
                min_floor=int(min_floor),
                max_floor=int(max_floor),
                description=description
            )
            db.session.add(building)
            db.session.commit()
            flash('楼栋添加成功', 'success')
            return redirect(url_for('classroom_bp.building_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('classroom/building_form.html')

@classroom_bp.route('/buildings/edit/<int:building_id>', methods=['GET', 'POST'])
@admin_required
def building_edit(building_id):
    building = Building.query.get_or_404(building_id)
    
    if request.method == 'POST':
        building.building_name = request.form.get('building_name', '').strip()
        building.campus = request.form.get('campus', '').strip()
        building.min_floor = int(request.form.get('min_floor', 1))
        building.max_floor = int(request.form.get('max_floor', 5))
        building.description = request.form.get('description', '').strip()
        
        try:
            db.session.commit()
            flash('楼栋信息更新成功', 'success')
            return redirect(url_for('classroom_bp.building_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('classroom/building_form.html', building=building)

@classroom_bp.route('/buildings/delete/<int:building_id>')
@admin_required
def building_delete(building_id):
    building = Building.query.get_or_404(building_id)
    
    if Classroom.query.filter_by(building_id=building_id).first():
        flash('该楼栋下存在教室，无法删除', 'danger')
        return redirect(url_for('classroom_bp.building_list'))
    
    try:
        db.session.delete(building)
        db.session.commit()
        flash('楼栋删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('classroom_bp.building_list'))

@classroom_bp.route('/')
@admin_required
def classroom_list():
    buildings = Building.query.all()
    building_id = request.args.get('building_id', type=int)
    
    query = Classroom.query
    if building_id:
        query = query.filter_by(building_id=building_id)
    
    classrooms = query.order_by(Classroom.classroom_code).all()
    return render_template('classroom/classroom_list.html', classrooms=classrooms, buildings=buildings, selected_building=building_id)

@classroom_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def classroom_add():
    buildings = Building.query.all()
    
    if request.method == 'POST':
        classroom_code = request.form.get('classroom_code', '').strip()
        building_id = request.form.get('building_id', type=int)
        floor = request.form.get('floor', type=int)
        capacity = request.form.get('capacity', 30)
        has_projector = request.form.get('has_projector') == 'on'
        has_computer = request.form.get('has_computer') == 'on'
        description = request.form.get('description', '').strip()
        
        if not classroom_code:
            flash('教室编号不能为空', 'danger')
            return render_template('classroom/classroom_form.html', buildings=buildings)
        
        if Classroom.query.filter_by(classroom_code=classroom_code).first():
            flash('该教室编号已存在', 'danger')
            return render_template('classroom/classroom_form.html', buildings=buildings)
        
        try:
            classroom = Classroom(
                classroom_code=classroom_code,
                building_id=building_id,
                floor=floor,
                capacity=int(capacity),
                has_projector=has_projector,
                has_computer=has_computer,
                description=description
            )
            db.session.add(classroom)
            db.session.commit()
            flash('教室添加成功', 'success')
            return redirect(url_for('classroom_bp.classroom_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'danger')
    
    return render_template('classroom/classroom_form.html', buildings=buildings)

@classroom_bp.route('/edit/<int:classroom_id>', methods=['GET', 'POST'])
@admin_required
def classroom_edit(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    buildings = Building.query.all()
    
    if request.method == 'POST':
        classroom.building_id = request.form.get('building_id', type=int)
        classroom.floor = request.form.get('floor', type=int)
        classroom.capacity = int(request.form.get('capacity', 30))
        classroom.has_projector = request.form.get('has_projector') == 'on'
        classroom.has_computer = request.form.get('has_computer') == 'on'
        classroom.status = 1 if request.form.get('status') == 'on' else 0
        classroom.description = request.form.get('description', '').strip()
        
        try:
            db.session.commit()
            flash('教室信息更新成功', 'success')
            return redirect(url_for('classroom_bp.classroom_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'danger')
    
    return render_template('classroom/classroom_form.html', classroom=classroom, buildings=buildings)

@classroom_bp.route('/delete/<int:classroom_id>')
@admin_required
def classroom_delete(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    if Schedule.query.filter_by(classroom=classroom.classroom_code).first():
        flash('该教室存在排课记录，无法删除', 'danger')
        return redirect(url_for('classroom_bp.classroom_list'))
    
    try:
        db.session.delete(classroom)
        db.session.commit()
        flash('教室删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')
    
    return redirect(url_for('classroom_bp.classroom_list'))

@classroom_bp.route('/schedule')
@admin_required
def schedule_manage():
    schedules = Schedule.query.join(Course).all()
    return render_template('classroom/schedule_manage.html', schedules=schedules)