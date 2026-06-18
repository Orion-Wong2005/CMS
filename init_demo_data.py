"""
初始化数据脚本
用于初始化系统的基础数据
"""
from app import create_app
from app.extensions import db
from app.models import User, Student, Teacher, Building, Classroom
from app.utils.md5 import md5_encrypt

def init_data():
    """初始化基础数据"""
    app = create_app()
    
    with app.app_context():
        # 清空现有数据（可选，取消注释以重新初始化）
        # User.query.delete()
        # Student.query.delete()
        # Teacher.query.delete()
        # Classroom.query.delete()
        # Building.query.delete()
        # db.session.commit()
        
        print("=" * 50)
        print("开始初始化数据...")
        print("=" * 50)
        
        # 1. 创建管理员账户
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=md5_encrypt('admin'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ 管理员账户已创建: admin / admin")
        else:
            print("ℹ 管理员账户已存在")
        
        # 2. 创建两栋教学楼
        buildings_data = [
            {'code': 'VA', 'name': '虚拟综合楼A'},
            {'code': 'VN', 'name': '虚拟综合楼N'}
        ]
        
        for b_data in buildings_data:
            if not Building.query.filter_by(building_code=b_data['code']).first():
                building = Building(
                    building_code=b_data['code'],
                    building_name=b_data['name'],
                    campus='主校区',
                    min_floor=-2,
                    max_floor=10,
                    description='系统初始化创建'
                )
                db.session.add(building)
                db.session.flush()
                
                # 为每栋楼创建教室：-2到10层，每层20个教室
                # 教室编码规则：楼号 + 层数 + 计数码
                # 例如：VA1001 = 虚拟A楼10层1号教室，VB201 = 虚拟A楼地下2层1号教室
                for floor in range(-2, 11):  # -2 到 10
                    if floor == 0 : continue
                    for room_num in range(1, 21):  # 每层20个教室
                        # 处理楼层编码
                        if floor < 0:
                            # 负楼层用B表示地下，后面跟绝对值（一位数）
                            floor_str = f"B{abs(floor)}"
                        else:
                            # 正楼层直接用数字（两位数，不足补0）
                            floor_str = f"{floor:02d}"
                        
                        # 教室编码：楼号 + 楼层 + 计数码(两位)
                        room_code = f"{b_data['code']}{floor_str}{room_num:02d}"
                        
                        # 检查是否已存在
                        if not Classroom.query.filter_by(classroom_code=room_code).first():
                            classroom = Classroom(
                                classroom_code=room_code,
                                building_id=building.id,
                                floor=floor,
                                capacity=50,
                                has_projector=1,  # 每3个教室有投影仪
                                has_computer=1,   # 每4个教室有电脑
                                status=1,
                                description='系统初始化创建'
                            )
                            db.session.add(classroom)
                
                db.session.commit()
                print(f"✓ 楼栋 '{b_data['name']}' 已创建，包含 {(10 - (-2) + 1) * 20} 个教室")
                print(f"  教室编码示例：VA0101(VA楼1层1号), VA1001(VA楼10层1号), VB201(VA楼地下2层1号)")
            else:
                print(f"ℹ 楼栋 '{b_data['name']}' 已存在")
        
        # 3. 创建学生账户
        students_data = [
            {'username': 'test001stu', 'name': '虚拟学生男', 'gender': '男', 'student_id': '202611201001'},
            {'username': 'test002stu', 'name': '虚拟学生女', 'gender': '女', 'student_id': '202611202001'}
        ]
        
        for s_data in students_data:
            # 检查用户是否已存在
            existing_user = User.query.filter_by(username=s_data['username']).first()
            
            if not existing_user:
                # 创建新用户
                user = User(
                    username=s_data['username'],
                    password=md5_encrypt(s_data['username']),
                    role='student'
                )
                db.session.add(user)
                db.session.flush()
                print(f"✓ 用户 '{s_data['username']}' 已创建")
            else:
                user = existing_user
                print(f"ℹ 用户 '{s_data['username']}' 已存在")
            
            # 检查学生记录是否已存在
            existing_student = Student.query.filter_by(student_id=s_data['student_id']).first()
            
            if existing_student:
                # 更新现有学生记录的user_id
                existing_student.user_id = user.id
                existing_student.name = s_data['name']
                existing_student.gender = s_data['gender']
                existing_student.major = '计算机科学与技术'
                existing_student.class_name = '计算机24级1班'
                db.session.commit()
                print(f"✓ 学生记录 '{s_data['student_id']}' 已更新")
            else:
                # 创建新学生记录
                student = Student(
                    student_id=s_data['student_id'],
                    name=s_data['name'],
                    gender=s_data['gender'],
                    major='计算机科学与技术',
                    class_name='计算机24级1班',
                    user_id=user.id
                )
                db.session.add(student)
                db.session.commit()
                print(f"✓ 学生记录 '{s_data['student_id']}' 已创建")
        
        # 4. 创建教师账户
        teachers_data = [
            {'username': 'test001tea', 'name': '虚拟教师男', 'gender': '男', 'title': '教授', 'teacher_id': '202621201001'},
            {'username': 'test002tea', 'name': '虚拟教师女', 'gender': '女', 'title': '副教授', 'teacher_id': '202621202001'}
        ]
        
        for t_data in teachers_data:
            # 检查用户是否已存在
            existing_user = User.query.filter_by(username=t_data['username']).first()
            
            if not existing_user:
                # 创建新用户
                user = User(
                    username=t_data['username'],
                    password=md5_encrypt(t_data['username']),
                    role='teacher'
                )
                db.session.add(user)
                db.session.flush()
                print(f"✓ 用户 '{t_data['username']}' 已创建")
            else:
                user = existing_user
                print(f"ℹ 用户 '{t_data['username']}' 已存在")
            
            # 检查教师记录是否已存在
            existing_teacher = Teacher.query.filter_by(teacher_id=t_data['teacher_id']).first()
            
            if existing_teacher:
                # 更新现有教师记录的user_id
                existing_teacher.user_id = user.id
                existing_teacher.name = t_data['name']
                existing_teacher.gender = t_data['gender']
                existing_teacher.department = '计算机学院'
                existing_teacher.title = t_data['title']
                db.session.commit()
                print(f"✓ 教师记录 '{t_data['teacher_id']}' 已更新")
            else:
                # 创建新教师记录
                teacher = Teacher(
                    teacher_id=t_data['teacher_id'],
                    name=t_data['name'],
                    gender=t_data['gender'],
                    department='计算机学院',
                    title=t_data['title'],
                    user_id=user.id
                )
                db.session.add(teacher)
                db.session.commit()
                print(f"✓ 教师记录 '{t_data['teacher_id']}' 已创建")
        
        print("=" * 50)
        print("数据初始化完成！")
        print("=" * 50)
        print("\n学号/工号规则说明：")
        print("  年份(4位) + 身份码(1位) + 学院码(2位) + 专业码(2位) + 计数码(3位)")
        print("  例如：202611201001")
        print("    - 2026: 2026年注册")
        print("    - 1: 学生身份 (2为教师)")
        print("    - 12: 计算机学院")
        print("    - 01: 计算机科学与技术专业")
        print("    - 001: 本专业第1个注册")
        print()

if __name__ == '__main__':
    init_data()
