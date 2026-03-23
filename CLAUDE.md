# CLAUDE.md — 应用管理系统

## 项目概览

前后端分离的应用管理平台，前端 Vue 3 + Element Plus，后端 Django 4.2 + MySQL 8。

## 目录结构

```
cicd/
├── backend/          # Django 后端（端口 8000）
│   ├── config.ini    # 数据库及服务器配置（勿提交密码）
│   ├── init_db.py    # 一次性数据库初始化脚本
│   ├── manage.py
│   ├── cicd_backend/ # Django 项目配置
│   └── apps/         # 业务模块（models / views / serializers / urls）
└── frontend/         # Vue 3 前端（端口 5173）
    └── src/
        ├── api/      # axios 封装
        ├── router/   # vue-router
        └── views/    # UserLogin / AdminLogin / AppList
```

## 环境与依赖

- Python 3.14，使用 `py` 命令执行（非 `python`）
- 包安装路径：`C:/Users/Admin/Documents/cicd/Lib/site-packages`
- Node.js 24，npm 11
- MySQL 8.0.44，host `127.0.0.1:3306`，user `root`

## 常用命令

```bash
# 后端启动
py C:/Users/Admin/Documents/cicd/backend/manage.py runserver

# 数据库迁移
py C:/Users/Admin/Documents/cicd/backend/manage.py makemigrations apps
py C:/Users/Admin/Documents/cicd/backend/manage.py migrate

# 前端启动（需在独立终端运行）
cd C:/Users/Admin/Documents/cicd/frontend && npm run dev
```

> 注意：所有 Django 命令必须用绝对路径执行，`cd` 到子目录后 site-packages 路径会丢失。

## 数据库

- 数据库名：`cicd`
- 密码配置在 `backend/config.ini`（`Wwh@12345`）
- 核心表：`app_info`（应用）、`user_info`（用户，密码 MD5 存储）
- Django 使用 PyMySQL 驱动，在 `cicd_backend/__init__.py` 中 `install_as_MySQLdb()`

## API 路由

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/login/` | 登录，body 含 `role: user\|admin` |
| GET/POST | `/api/apps/` | 应用列表 / 新建 |
| GET/PUT/DELETE | `/api/apps/<id>/` | 应用详情 / 更新 / 删除 |
| GET/POST | `/api/users/` | 用户列表 / 新建 |
| GET/PUT/DELETE | `/api/users/<id>/` | 用户详情 / 更新 / 删除 |

## 已知账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin  | admin | 管理员 |

## Git 配置

### 代理设置

由于网络环境限制，需要配置代理才能访问 GitHub：

```bash
# 配置 HTTP 代理（推荐）
git config --global http.proxy http://127.0.0.1:7890

# 取消代理配置
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 提交代码流程

```bash
# 1. 查看状态
git status

# 2. 添加文件
git add <文件路径>

# 3. 提交
git commit -m "提交信息

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# 4. 推送到远程
git push
```

## 注意事项

- 前端 vite 已配置 `/api` 代理到 `http://127.0.0.1:8000`，后端必须先启动
- 不要运行 `npm run dev` 等长期进程作为后台任务，告知用户手动执行
- 修改 models 后必须重新执行 `makemigrations` + `migrate`
- 表一定包含以下字段，并且需要实现对应逻辑
    - deleted 假删除
    - create_time 创建时间
    - update_time 更新时间
- 生成列表接口的时候有分页功能
- Git 推送大文件时可能需要配置代理，使用 `http://127.0.0.1:7890`
