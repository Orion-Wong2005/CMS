# 课程管理系统

一个基于 Flask 的完整课程管理系统，支持管理员、教师和学生三种角色的用户。

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [安装步骤](#安装步骤)
  - [Windows本地部署超详细步骤](#windows本地部署超详细步骤)
- [使用说明](#使用说明)
  - [默认账号](#默认账号)
  - [管理员操作指南](#管理员操作指南)
  - [教师操作指南](#教师操作指南)
  - [学生操作指南](#学生操作指南)
- [技术说明](#技术说明)
  - [密码加密规则](#密码加密规则)
  - [项目结构](#项目结构)
  - [数据库模型](#数据库模型)
- [CI/CD](#cicd)
- [常见问题](#常见问题)
- [系统维护](#系统维护)

---

## 功能特性

### 管理员功能
- 学生信息管理（添加、编辑、删除、查询）
- 教师信息管理（添加、编辑、删除、查询）
- 课程信息管理（添加、编辑、删除、查询）
- 排课管理
- 用户权限控制

### 教师功能
- 查看所授课程
- 查看课程学生名单
- 录入和修改学生成绩（单个/批量）
- 导出成绩表
- 查看个人课表

### 学生功能
- 查看课程信息
- 课程选课和退课
- 查看已选课程
- 查询个人成绩与绩点
- 查看个人课表

### 通用功能
- 用户登录/退出
- 密码修改
- 权限控制

---

## 技术栈

- **后端框架**：Flask 2.3.3
- **数据库 ORM**：Flask-SQLAlchemy 3.1.1
- **数据库迁移**：Flask-Migrate 4.0.7
- **模板引擎**：Jinja2 3.1.2
- **数据库**：SQLite（开发）/ MySQL（生产）
- **前端**：HTML + CSS + JavaScript + Bootstrap 5
- **CI/CD**：GitHub Actions

---

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装步骤

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **初始化数据库**
   ```bash
   # 应用迁移，创建所有表（migrations 已包含在仓库中）
   flask db upgrade
   ```

3. **初始化示例数据**
   ```bash
   python init_data.py
   ```

4. **运行系统**
   ```bash
   python run.py
   ```

5. **访问系统**
   - 浏览器访问：`http://localhost:5000/auth/login`

---

### Windows本地部署超详细步骤

#### 📋 前置说明
- **适用系统**：Windows 10/11（64位）
- **最终效果**：在你的电脑上运行完整的课程管理系统，可通过浏览器访问

#### 🔧 第一步：安装必备软件

##### 1. 安装Python 3.10（推荐版本，兼容性最好）
1. 下载地址：https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
2. 运行安装程序，**务必勾选最下方的 "Add Python 3.10 to PATH"**
3. 点击 "Install Now" 完成安装
4. 验证安装：
   ```bash
   python --version
   pip --version
   ```

##### 2. 安装MySQL 8.0（数据库，可选，默认使用SQLite）
1. 下载地址：https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.36.0.msi
2. 运行安装程序，选择 "Developer Default"，点击 Next
3. 一路点击 Next，直到 "Authentication Method" 页面，选择 **"Use Legacy Authentication Method"**
4. 设置MySQL root用户密码（请记住这个密码）
5. 一路点击 Next，最后点击 Execute 完成安装

#### 🗄️ 第二步：创建数据库（仅使用MySQL时需要）
1. 打开MySQL命令行
2. 输入root密码，登录MySQL
3. 执行以下命令：
   ```sql
   CREATE DATABASE IF NOT EXISTS course_management_system
   DEFAULT CHARACTER SET utf8mb4
   DEFAULT COLLATE utf8mb4_unicode_ci;
   ```
4. 输入 `exit` 退出MySQL

#### 📂 第三步：准备项目代码
1. 将项目文件夹放到一个**没有中文和空格**的路径下
   - ✅ 正确路径：`D:\projects\course_management_system`
   - ❌ 错误路径：`D:\我的项目\课程管理系统`
2. 确认项目根目录下有 `app/`、`run.py`、`requirements.txt`

#### 🐍 第四步：创建Python虚拟环境（推荐）
1. 打开项目文件夹，在地址栏输入 `cmd`，按回车
2. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
3. 激活虚拟环境：
   ```bash
   venv\Scripts\activate
   ```
4. 成功激活后，命令行前面会出现 `(venv)` 标识

#### 📦 第五步：安装项目依赖
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
- 使用清华镜像源，下载速度更快

#### ⚙️ 第六步：修改数据库配置（使用MySQL时需要）
1. 打开 `app/config.py` 文件
2. 修改数据库连接字符串：
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:你的MySQL密码@localhost:3306/course_management_system'
   ```
3. 保存文件

#### 🗃️ 第七步：初始化数据库表
```bash
flask db upgrade
```

#### 🚀 第八步：运行系统
```bash
python init_data.py  # 初始化示例数据
python run.py        # 启动系统
```

看到以下输出即表示启动成功：
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

#### 🌐 第九步：访问系统
浏览器访问：`http://localhost:5000/auth/login`

---

## 使用说明

### 默认账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| **管理员** | `admin` | `123456` | 系统默认超级管理员 |
| **教师** | `teacher` | `123456` | 示例教师账号 |
| **学生** | `student` | `123456` | 示例学生账号 |

> 注意：管理员添加学生/教师时，会自动创建登录账号，用户名=学号/工号，默认密码=学号/工号

---

### 管理员操作指南

#### 登录系统
1. 打开系统登录页面
2. 输入管理员用户名和密码
3. 点击"登录"按钮，进入管理员控制台

#### 学生管理
- **添加学生**：点击"学生管理" → "添加学生" → 填写信息 → 保存
- **编辑学生**：在学生列表中点击"编辑" → 修改信息 → 保存
- **删除学生**：点击"删除" → 确认删除

#### 教师管理
操作流程与学生管理完全一致。

#### 课程管理
- **添加课程**：点击"课程管理" → "添加课程" → 填写课程信息 → 选择授课教师 → 保存
- **编辑/删除课程**：在课程列表中进行相应操作

#### 排课管理
- **添加排课**：点击"排课管理" → "添加排课" → 选择课程、时间、教室 → 保存
- 系统会自动检查教室冲突和教师时间冲突

---

### 教师操作指南

#### 查看我的课程
- 点击"我的课程"，查看所有自己教授的课程

#### 查看课程学生名单
- 在"我的课程"中，点击课程右侧"查看学生"

#### 成绩录入
- **单个录入**：在学生名单中，点击"录入"或"修改"按钮
- **批量录入**：点击"批量录入成绩"按钮，一次性输入所有成绩
- **导出成绩**：点击"导出成绩表"，自动生成Excel文件下载

#### 查看我的课表
- 点击"我的课表"，查看以周为单位的个人课表

---

### 学生操作指南

#### 选课中心
1. 点击"选课中心"，查看所有可选课程
2. 对于未满且未选的课程，点击"选课"按钮
3. 确认后完成选课

#### 我的课程
- 查看所有已选课程
- 对于未出成绩的课程，可以点击"退课"

#### 我的成绩
- 查看所有已出成绩的课程
- 页面顶部显示已修学分和平均绩点(GPA)

#### 我的课表
- 查看以周为单位的个人课表

---

### 通用功能

#### 修改密码
1. 点击右上角用户名下拉菜单
2. 选择"修改密码"
3. 输入旧密码、新密码和确认新密码
4. 点击"确认修改"

#### 退出登录
1. 点击右上角用户名下拉菜单
2. 选择"退出登录"

---

## 技术说明

### 密码加密规则

系统使用 **MD5 32位小写加密**存储用户密码。

**加密示例**：
- 明文：`123456`
- MD5加密结果：`e10adc3949ba59abbe56e057f20f883e`

**Python实现**（`app/utils/md5.py`）：
```python
import hashlib

def md5_encrypt(password: str) -> str:
    """MD5 32位小写加密"""
    return hashlib.md5(password.encode('utf-8')).hexdigest().lower()
```

**登录校验**：
用户输入密码 → MD5加密 → 与数据库密文对比 → 一致则登录成功

---

### 项目结构

```
CMS-main/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD 配置
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── config.py                # 配置文件
│   ├── extensions.py            # Flask扩展初始化
│   ├── blueprints/              # 蓝图（路由）
│   │   ├── auth.py              # 认证模块
│   │   ├── admin.py             # 管理员模块
│   │   ├── teacher.py           # 教师模块
│   │   ├── student.py           # 学生模块
│   │   ├── course.py            # 课程模块
│   │   ├── enrollment.py        # 选课模块
│   │   ├── grade.py             # 成绩模块
│   │   └── schedule.py          # 排课模块
│   ├── models/                  # 数据模型
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── teacher.py
│   │   ├── course.py
│   │   ├── enrollment.py
│   │   ├── grade.py
│   │   └── schedule.py
│   ├── templates/               # HTML模板
│   │   ├── admin/
│   │   ├── teacher/
│   │   ├── student/
│   │   ├── auth/
│   │   ├── common/
│   │   └── base.html
│   ├── static/                  # 静态资源
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/                   # 工具函数
├── docs/                        # 项目文档
│   ├── 学生端关键功能说明.md
│   ├── 密码加密规则.md
│   ├── 模型使用说明.txt
│   ├── 登录认证模块关键功能说明.md
│   ├── 管理员后台关键功能说明.md
│   ├── 系统运行测试手册.md
│   ├── 课程管理系统 MySQL 建表语句.sql
│   ├── 课程管理系统V2.0使用说明书.md
│   └── 项目目录结构.plaintext
├── migrations/                  # 数据库迁移文件
├── init_data.py                 # 初始化数据脚本
├── requirements.txt             # Python依赖（锁定版本）
├── .gitignore                   # Git 忽略文件
├── README.md                    # 项目说明文档
└── run.py                       # 启动脚本
```

---

### 数据库模型

系统包含以下主要数据模型：

- **User**：用户账户
- **Student**：学生信息
- **Teacher**：教师信息
- **Course**：课程信息
- **Enrollment**：选课记录
- **Grade**：成绩记录
- **Schedule**：排课信息

---

## CI/CD

本项目使用 GitHub Actions 实现自动化测试和部署检查。

### CI 流程

1. **触发条件**
   - 推送代码到 main/master 分支
   - 创建 Pull Request 到 main/master 分支

2. **测试矩阵**
   - Python 3.9
   - Python 3.10
   - Python 3.11

3. **测试步骤**
   - 代码检出
   - Python 环境设置
   - 依赖安装（带缓存）
   - Lint 检查
   - 应用启动测试

4. **部署检查**
   - 主分支测试通过后运行
   - 验证生产就绪状态

### 查看 CI 状态

在 GitHub 仓库页面可以看到 CI 运行状态的徽章。

---

## 常见问题

### Q1：`python` 不是内部或外部命令
- 原因：安装Python时没有勾选 "Add Python to PATH"
- 解决：重新运行Python安装程序，勾选该选项

### Q2：数据库连接失败
- 原因1：MySQL服务没有启动
  - 解决：按 `Win+R` 输入 `services.msc`，找到 "MySQL80" 服务，右键启动
- 原因2：密码错误
  - 解决：确认 `app/config.py` 中的密码和你设置的MySQL root密码一致

### Q3：`flask` 不是内部或外部命令
- 原因：没有激活虚拟环境，或者依赖没有安装成功
- 解决：重新激活虚拟环境，然后重新安装依赖

### Q4：端口5000被占用
- 原因：其他程序占用了5000端口
- 解决：修改 `run.py` 文件，将端口改为其他未被占用的端口（比如5001）

### Q5：登录时提示"用户名或密码错误"
- 检查用户名和密码是否输入正确，注意区分大小写
- 学生用户名是学号，教师用户名是工号
- 初始密码与用户名相同

### Q6：选课失败，提示"课程容量已满"
- 该课程选课人数已达到上限
- 可以选择其他未满的课程

### Q7：无法退课
- 已出成绩的课程不允许退课
- 请联系管理员处理特殊情况

---

## 系统维护

### 数据库备份

#### Windows本地备份（SQLite）
直接备份 `cms.db` 文件即可。

#### Windows本地备份（MySQL）
```bash
mysqldump -u root -p course_management_system > backup_YYYYMMDD.sql
```

#### Linux服务器备份（MySQL）
```bash
mysqldump -u cms_user -p course_management_system > backup_YYYYMMDD.sql
```

### 数据库恢复

#### Windows本地恢复（SQLite）
将备份文件覆盖 `cms.db` 即可。

#### Windows本地恢复（MySQL）
```bash
mysql -u root -p course_management_system < backup_YYYYMMDD.sql
```

#### Linux服务器恢复（MySQL）
```bash
mysql -u cms_user -p course_management_system < backup_YYYYMMDD.sql
```

### 日常维护
- 定期修改管理员密码，确保系统安全
- 定期清理无用的学生、教师和课程数据
- 定期备份数据库，建议每周备份一次
- 及时更新系统依赖包，修复安全漏洞

---

## 许可证

MIT License
