from app import create_app
from app.extensions import db
from app.models import User, Student, Teacher, Course
from app.utils.md5 import md5_encrypt

def init_data():
    """初始化系统数据"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已有数据
        if User.query.first():
            print('系统已有数据，无需初始化！')
            return
        
        print('开始初始化系统数据...')
        
        # 1. 创建管理员账号
        admin = User(
            username='admin',
            password=md5_encrypt('123456'),
            role='admin'
        )
        db.session.add(admin)
        
        # 2. 创建教师账号
        teacher_user = User(
            username='teacher',
            password=md5_encrypt('123456'),
            role='teacher'
        )
        db.session.add(teacher_user)
        
        teacher = Teacher(
            teacher_id='T001',
            name='张老师',
            gender='男',
            department='计算机学院',
            title='副教授',
            phone='13800138001',
            email='teacher@example.com'
        )
        teacher.user = teacher_user
        db.session.add(teacher)
        
        # 3. 创建学生账号
        student_user = User(
            username='student',
            password=md5_encrypt('123456'),
            role='student'
        )
        db.session.add(student_user)
        
        student = Student(
            student_id='S001',
            name='李同学',
            gender='男',
            major='软件工程',
            class_name='软工2201',
            phone='13900139001',
            email='student@example.com'
        )
        student.user = student_user
        db.session.add(student)
        
        # 4. 创建示例课程
        course1 = Course(
            course_id='C001',
            course_name='Python程序设计',
            credit=3.0,
            hours=48,
            teacher_id='T001',
            semester='2024-2025-1',
            capacity=50
        )
        db.session.add(course1)
        
        course2 = Course(
            course_id='C002',
            course_name='数据库原理',
            credit=4.0,
            hours=64,
            teacher_id='T001',
            semester='2024-2025-1',
            capacity=40
        )
        db.session.add(course2)
        
        # 提交数据
        db.session.commit()
        
        print('=' * 50)
        print('✅ 数据初始化完成！')
        print('=' * 50)
        print('可用账号：')
        print('  管理员: admin / 123456')
        print('  教师:   teacher / 123456')
        print('  学生:   student / 123456')
        print('=' * 50)

if __name__ == '__main__':
    init_data()
