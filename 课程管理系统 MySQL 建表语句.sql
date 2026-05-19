-- 创建数据库
CREATE DATABASE IF NOT EXISTS course_management_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE course_management_system;

-- 1. 用户表
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(30) NOT NULL UNIQUE COMMENT '登录账号',
    password VARCHAR(64) NOT NULL COMMENT '登录密码',
    role ENUM('admin','teacher','student') NOT NULL DEFAULT 'student' COMMENT '角色',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- 2. 学生表
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY COMMENT '学号',
    name VARCHAR(20) NOT NULL COMMENT '姓名',
    gender CHAR(2) COMMENT '性别',
    major VARCHAR(50) COMMENT '专业',
    class_name VARCHAR(50) COMMENT '班级',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(50) COMMENT '邮箱',
    user_id INT UNIQUE COMMENT '关联用户ID',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表';

-- 3. 教师表
DROP TABLE IF EXISTS teachers;
CREATE TABLE teachers (
    teacher_id VARCHAR(20) PRIMARY KEY COMMENT '工号',
    name VARCHAR(20) NOT NULL COMMENT '姓名',
    gender CHAR(2) COMMENT '性别',
    department VARCHAR(50) COMMENT '所属院系',
    title VARCHAR(30) COMMENT '职称',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(50) COMMENT '邮箱',
    user_id INT UNIQUE COMMENT '关联用户ID',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师信息表';

-- 4. 课程表
DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    course_id VARCHAR(20) PRIMARY KEY COMMENT '课程编号',
    course_name VARCHAR(50) NOT NULL COMMENT '课程名称',
    credit DECIMAL(3,1) NOT NULL COMMENT '学分',
    hours INT NOT NULL COMMENT '学时',
    teacher_id VARCHAR(20) COMMENT '授课教师工号',
    semester VARCHAR(30) COMMENT '开课学期',
    capacity INT DEFAULT 60 COMMENT '选课人数上限',
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程信息表';

-- 5. 选课表
DROP TABLE IF EXISTS enrollments;
CREATE TABLE enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL COMMENT '学号',
    course_id VARCHAR(20) NOT NULL COMMENT '课程编号',
    enroll_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    status TINYINT DEFAULT 1 COMMENT '状态 1正常 0退课',
    UNIQUE KEY uk_stu_course (student_id,course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生选课表';

-- 6. 成绩表
DROP TABLE IF EXISTS grades;
CREATE TABLE grades (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL COMMENT '学号',
    course_id VARCHAR(20) NOT NULL COMMENT '课程编号',
    grade DECIMAL(5,1) COMMENT '考试成绩',
    remark VARCHAR(100) COMMENT '备注',
    UNIQUE KEY uk_stu_course_grade (student_id,course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生成绩表';

-- 7. 排课表
DROP TABLE IF EXISTS schedules;
CREATE TABLE schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(20) NOT NULL COMMENT '课程编号',
    day_of_week TINYINT COMMENT '星期1-7',
    start_time VARCHAR(20) COMMENT '开始时间',
    end_time VARCHAR(20) COMMENT '结束时间',
    classroom VARCHAR(30) COMMENT '上课教室',
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程排课表';

-- 初始化管理员账号 账号:admin 密码:123456(加密后)
INSERT INTO users(username,password,role) VALUES ('admin','e10adc3949ba59abbe56e057f20f883e','admin');
