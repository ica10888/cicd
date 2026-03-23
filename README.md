# 应用管理系统

基于 Vue 3 + Django 的前后端分离应用管理平台，支持普通用户和管理员两种角色。

## 项目结构

```
cicd/
├── backend/                # Django 后端
│   ├── config.ini          # 数据库及服务配置
│   ├── init_db.py          # 数据库初始化脚本
│   ├── manage.py
│   ├── requirements.txt
│   ├── cicd_backend/       # Django 项目配置
│   │   ├── settings.py
│   │   └── urls.py
│   └── apps/               # 业务模块
│       ├── models.py       # 数据模型（AppInfo / UserInfo）
│       ├── serializers.py
│       ├── views.py        # CRUD + 登录接口
│       └── urls.py
└── frontend/               # Vue 3 前端
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── api/index.js    # axios 接口封装
        ├── router/index.js
        └── views/
            ├── UserLogin.vue   # 普通用户登录
            ├── AdminLogin.vue  # 管理员登录
            └── AppList.vue     # 应用列表
```

## 环境要求

| 依赖 | 版本 |
|------|------|
| Python | >= 3.9 |
| Node.js | >= 18 |
| MySQL | >= 5.7 |

## 快速启动

### 1. 配置数据库

编辑 `backend/config.ini`：

```ini
[database]
host = 127.0.0.1
port = 3306
user = root
password = WWH@12345
name = cicd
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（自动创建 cicd 库）
python init_db.py

# 生成并执行数据库迁移（自动建表）
python manage.py makemigrations apps
python manage.py migrate

# 启动开发服务器（默认 8000 端口）
python manage.py runserver
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认 5173 端口）
npm run dev
```

访问 http://localhost:5173

## 页面说明

| 路由 | 页面 | 说明 |
|------|------|------|
| `/login` | 普通用户登录 | 紫色主题，登录后可查看应用列表 |
| `/admin/login` | 管理员登录 | 红色主题，登录后可增删改应用 |
| `/apps` | 应用列表 | 展示所有应用，管理员有操作权限 |

## API 接口

### 认证

```
POST /api/login/
Body: { "username": "", "password": "", "role": "user|admin" }
```

### 应用管理

```
GET    /api/apps/          # 获取应用列表
POST   /api/apps/          # 新建应用
GET    /api/apps/<id>/     # 获取应用详情
PUT    /api/apps/<id>/     # 更新应用
DELETE /api/apps/<id>/     # 删除应用
```

### 用户管理

```
GET    /api/users/         # 获取用户列表
POST   /api/users/         # 新建用户
GET    /api/users/<id>/    # 获取用户详情
PUT    /api/users/<id>/    # 更新用户
DELETE /api/users/<id>/    # 删除用户
```

## 数据模型

### AppInfo（应用表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt | 主键 |
| name | VARCHAR(100) | 应用名称（唯一） |
| description | TEXT | 描述 |
| version | VARCHAR(50) | 版本号 |
| status | VARCHAR(20) | 状态：running / stopped / deploying / error |
| repo_url | VARCHAR(255) | 仓库地址 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### UserInfo（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| password | VARCHAR(255) | MD5 加密密码 |
| email | VARCHAR(254) | 邮箱 |
| role | VARCHAR(20) | 角色：admin / user |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
