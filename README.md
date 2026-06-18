# 课程管理系统

基于 Flask + MySQL + Bootstrap 开发的高校课程管理系统，支持管理员、教师、学生三种角色，提供课程管理、选课、成绩管理、排课等功能。

---

## 一、功能特性

### 🔐 用户管理
- 用户登录/退出
- 角色权限控制（管理员、教师、学生）
- 密码修改

### 👨‍🎓 学生管理
- 学生信息增删改查
- 学号自动生成（年份+身份码+学院码+专业码+计数码）
- 学生账户初始化

### 👨‍🏫 教师管理
- 教师信息增删改查
- 职称管理（助教、讲师、副教授、教授）

### 📚 课程管理
- 课程信息增删改查
- 学期管理
- 学分设置

### 📝 选课管理
- 学生选课/退课
- 选课人数限制
- 选课状态管理

### 📊 成绩管理
- 教师录入/修改成绩
- 学生查询成绩
- 绩点计算
- 成绩导出（CSV）

### 🏫 教室管理
- 教学楼管理
- 教室管理（编码规则：楼号+层数+计数码）
- 排课管理

### 📅 课表管理
- 学生课表查看
- 教师课表查看
- 课表导出（CSV）

---

## 二、技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 框架 | Flask | 3.1.3 |
| 数据库 | MySQL | 8.0+ |
| ORM | SQLAlchemy | 2.0.31 |
| 前端 | Bootstrap | 5.x |
| 模板引擎 | Jinja2 | 3.1.6 |

---

## 三、依赖列表

### 核心依赖

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| Flask | 3.1.3 | Web 框架 |
| Flask-SQLAlchemy | 3.1.2 | ORM 框架 |
| Flask-Migrate | 4.1.1 | 数据库迁移 |
| PyMySQL | 1.2.0 | MySQL 驱动 |
| Werkzeug | 3.1.8 | WSGI 工具 |
| Jinja2 | 3.1.6 | 模板引擎 |

### 其他依赖

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| SQLAlchemy | 2.0.50 | ORM 核心 |
| alembic | 1.13.2 | 数据库迁移工具 |
| itsdangerous | 2.2.0 | 安全工具 |
| click | 8.1.7 | CLI 工具 |
| blinker | 1.9.0 | 信号库 |
| python-dateutil | 2.9.0 | 日期处理 |
| six | 1.16.0 | Python 2/3 兼容 |
| Mako | 1.3.2 | 模板引擎（迁移用） |
| markupsafe | 2.1.5 | 安全字符串处理 |
| openpyxl | 3.1.5 | Excel 处理 |
| et-xmlfile | 1.1.0 | XML 文件处理 |

---

## 四、项目结构

```
CMS-main/
├── app/                    # 应用目录
│   ├── blueprints/         # 蓝图路由模块
│   │   ├── admin.py        # 管理员模块
│   │   ├── auth.py         # 认证模块
│   │   ├── classroom.py    # 教室管理
│   │   ├── course.py       # 课程管理
│   │   ├── enrollment.py   # 选课管理
│   │   ├── grade.py        # 成绩管理
│   │   ├── schedule.py     # 排课管理
│   │   ├── semester.py     # 学期管理
│   │   ├── student.py      # 学生模块
│   │   └── teacher.py      # 教师模块
│   ├── models/             # 数据模型
│   ├── templates/          # HTML 模板
│   ├── static/             # 静态资源
│   ├── utils/              # 工具函数
│   ├── __init__.py         # 应用工厂
│   ├── config.py           # 配置文件
│   └── extensions.py       # 扩展初始化
├── migrations/             # 数据库迁移文件
├── init_demo_data.py       # 测试数据初始化
├── requirements.txt        # 依赖列表
├── run.py                  # 启动脚本
└── README.md               # 项目说明
```

---

## 五、环境要求

### 1. 操作系统
- Windows 10/11 (推荐)
- Linux (Ubuntu 20.04+/CentOS 7+)
- macOS 10.15+

### 2. Python 版本
- Python 3.8.x 或更高版本

### 3. 数据库
- MySQL 8.0.x 或更高版本

### 4. 端口要求
- 默认端口：5000（可在运行时修改）

---

## 六、部署步骤

### 步骤 1：安装 Python 环境

#### Windows
1. 下载 Python 安装包：https://www.python.org/downloads/windows/
2. 安装时勾选 "Add Python to PATH"
3. 验证安装：
   ```bash
   python --version
   pip --version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### macOS
```bash
brew install python3
```

### 步骤 2：安装 MySQL 数据库

#### Windows
1. 下载 MySQL Installer：https://dev.mysql.com/downloads/installer/
2. 安装时选择 "Developer Default" 或 "Server only"
3. 设置 root 用户密码（建议设置为 `123456`）

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 步骤 3：创建项目数据库

1. 登录 MySQL：
   ```bash
   mysql -u root -p
   ```

2. 创建数据库：
   ```sql
   CREATE DATABASE course_management_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. 创建用户并授权（可选）：
   ```sql
   CREATE USER 'cms_user'@'localhost' IDENTIFIED BY 'cms_password';
   GRANT ALL PRIVILEGES ON course_management_system.* TO 'cms_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### 步骤 4：配置项目

1. 进入项目目录：
   ```bash
   cd CMS-main
   ```

2. 修改数据库配置：
   - 打开 `app/config.py`
   - 修改数据库连接字符串：
     ```python
     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/course_management_system'
     ```
   - 替换 `root` 为你的 MySQL 用户名
   - 替换 `123456` 为你的 MySQL 密码

### 步骤 5：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 6：初始化数据库

```bash
python init_demo_data.py
```

此脚本会创建以下测试数据：
- 管理员账户：admin / admin
- 2 名学生账户
- 2 名教师账户
- 2 栋教学楼及其教室

### 步骤 7：启动服务

```bash
python run.py
```

### 步骤 8：访问系统

打开浏览器访问：http://localhost:5000

---

## 七、测试账户

| 角色 | 用户名 | 密码 | 姓名 |
|------|--------|------|------|
| 管理员 | admin | admin | - |
| 学生 | test001stu | test001stu | 虚拟学生男 |
| 学生 | test002stu | test002stu | 虚拟学生女 |
| 教师 | test001tea | test001tea | 虚拟教师男 |
| 教师 | test002tea | test002tea | 虚拟教师女 |

---

## 八、编码规则

### 学号/工号规则

```
年份(4位) + 身份码(1位) + 学院码(2位) + 专业码(2位) + 计数码(3位)

例如：202611201001
- 2026: 2026年注册
- 1: 学生身份 (2为教师)
- 12: 计算机学院
- 01: 计算机科学与技术专业
- 001: 本专业第1个注册
```

### 教室编码规则

```
楼号 + 层数 + 计数码

例如：VA1001
- VA: 楼号（VA、VN、B等）
- 10: 楼层（10层）
- 01: 教室编号
```

### 学期格式

格式：`XXXX-XXXX-X`

例如：`2026-2027-1` 表示 2026-2027学年第1学期

---

## 九、系统配置说明

### 配置文件位置
`app/config.py`

### 主要配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| SQLALCHEMY_DATABASE_URI | mysql+pymysql://... | 数据库连接字符串 |
| SQLALCHEMY_TRACK_MODIFICATIONS | False | 是否追踪修改 |
| SECRET_KEY | secret_key | 会话密钥 |
| DEBUG | True | 调试模式 |

### 修改配置示例

```python
class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://用户名:密码@localhost:3306/course_management_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SECRET_KEY = 'your-secret-key-here'
    
    # 调试模式（生产环境设置为 False）
    DEBUG = True
```

---

## 十、常见问题

### Q1：MySQL 连接失败
**现象**：
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1045, "Access denied for user 'root'@'localhost'")
```

**解决方案**：
1. 检查 MySQL 服务是否启动
2. 确认用户名和密码正确
3. 确保数据库 `course_management_system` 已创建

### Q2：端口被占用
**现象**：
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

**解决方案**：
```bash
# Windows
netstat -ano | findstr :5000
taskkill /F /PID <进程ID>

# Linux/macOS
lsof -i :5000
kill -9 <进程ID>
```

### Q3：依赖安装失败
**现象**：
```
ERROR: Could not install packages due to an OSError: [WinError 5] 拒绝访问
```

**解决方案**：
```bash
pip install -r requirements.txt --user
```

### Q4：数据库表不存在
**现象**：
```
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1146, "Table 'course_management_system.users' doesn't exist")
```

**解决方案**：
```bash
python init_demo_data.py
```

---

## 十一、生产环境部署建议

### 1. 使用 Gunicorn（Linux）
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 2. 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 关闭调试模式
修改 `app/config.py`：
```python
DEBUG = False
```

### 4. 设置防火墙规则（Linux）
```bash
sudo ufw allow 5000/tcp
sudo ufw enable
```

---

## 十二、许可证

MIT License

---

## 十三、版本信息

| 项目 | 版本 |
|------|------|
| 课程管理系统 | v2.0 |
| Flask | 3.1.3 |
| MySQL | 8.0+ |

---

**文档版本**: v1.0  
**生成日期**: 2026年6月  
**适用环境**: Windows/Linux/macOS
