-- ==============================
-- 课程管理系统 MySQL 完整建表脚本
-- 数据库：course_management_system
-- 编码：utf8mb4
-- ==============================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS course_management_system
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE course_management_system;

-- ----------------------------
-- 1. 系统用户表（登录账号）
-- ----------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(30) NOT NULL UNIQUE COMMENT '登录账号',
    password VARCHAR(64) NOT NULL COMMENT '密码(MD5加密)',
    role ENUM('admin','teacher','student') NOT NULL DEFAULT 'student' COMMENT '角色',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- ----------------------------
-- 2. 学生信息表
-- ----------------------------
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY COMMENT '学号',
    name VARCHAR(20) NOT NULL COMMENT '姓名',
    gender CHAR(2) COMMENT '性别',
    major VARCHAR(50) COMMENT '专业',
    class_name VARCHAR(50) COMMENT '班级',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(50) COMMENT '邮箱',
    user_id INT UNIQUE NOT NULL COMMENT '关联用户ID',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表';

-- ----------------------------
-- 3. 教师信息表
-- ----------------------------
DROP TABLE IF EXISTS teachers;
CREATE TABLE teachers (
    teacher_id VARCHAR(20) PRIMARY KEY COMMENT '工号',
    name VARCHAR(20) NOT NULL COMMENT '姓名',
    gender CHAR(2) COMMENT '性别',
    department VARCHAR(50) COMMENT '院系',
    title VARCHAR(30) COMMENT '职称',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(50) COMMENT '邮箱',
    user_id INT UNIQUE NOT NULL COMMENT '关联用户ID',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师信息表';

-- ----------------------------
-- 4. 课程信息表
-- ----------------------------
DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    course_id VARCHAR(20) PRIMARY KEY COMMENT '课程编号',
    course_name VARCHAR(100) NOT NULL COMMENT '课程名称',
    credit DECIMAL(3,1) NOT NULL COMMENT '学分',
    hours INT NOT NULL COMMENT '学时',
    teacher_id VARCHAR(20) COMMENT '授课教师工号',
    semester VARCHAR(30) COMMENT '开课学期',
    capacity INT DEFAULT 60 COMMENT '容量',
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
    INDEX idx_teacher_id (teacher_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程信息表';

-- ----------------------------
-- 5. 选课表
-- ----------------------------
DROP TABLE IF EXISTS enrollments;
CREATE TABLE enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL COMMENT '学号',
    course_id VARCHAR(20) NOT NULL COMMENT '课程编号',
    enroll_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    status TINYINT DEFAULT 1 COMMENT '1正常 0退课',
    UNIQUE KEY uk_student_course (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选课表';

-- ----------------------------
-- 6. 成绩表
-- ----------------------------
DROP TABLE IF EXISTS grades;
CREATE TABLE grades (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL COMMENT '学号',
    course_id VARCHAR(20) NOT NULL COMMENT '课程编号',
    grade DECIMAL(5,1) NULL COMMENT '成绩',
    remark VARCHAR(100) COMMENT '备注',
    UNIQUE KEY uk_student_course_grade (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成绩表';

-- ----------------------------
-- 7. 排课表
-- ----------------------------
DROP TABLE IF EXISTS schedules;
CREATE TABLE schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(20) NOT NULL COMMENT '课程编号',
    day_of_week TINYINT COMMENT '星期(1-7)',
    start_time VARCHAR(20) COMMENT '开始节次/时间',
    end_time VARCHAR(20) COMMENT '结束节次/时间',
    classroom VARCHAR(30) COMMENT '教室',
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='排课表';

-- ----------------------------
-- 初始化管理员账号
-- 账号：admin
-- 密码：123456（MD5加密）
-- ----------------------------
INSERT INTO users (username, password, role)
VALUES ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin');

-- ==============================
-- 建表完成
-- ==============================
