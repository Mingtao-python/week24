# AI Learning Platform V2

Week24 学习平台：Frontend → Backend → Permission → Model / Database → Response。

使用 HTML + JavaScript、FastAPI 和 SQLite。保留简单结构，先把权限和数据链路跑通。

# 1. Features

## Authentication 认证

- 注册固定创建 Student，不能通过请求指定 Admin。

- 登录返回 token + user_id + role。

- 注册、登录无需 token；学习计划、进度、分配和模型接口需要 token。

## Authorization 权限

- Student：自己的学习计划和进度。

- Teacher：已分配学生的学习计划和进度。

- Admin：可访问学习数据；管理用户角色 / 密码并分配 Teacher。

- 分配前检查两个账号存在，且角色分别是 Teacher / Student。

- 页面隐藏按钮只改善使用体验。权限由 Backend 检查。

## StudyPlan 学习计划

- Create：保存新计划。

- Read：查看最新保存的计划。

- 空白或超过 1000 字符 → 400。

## Progress 学习进度

- Update：按 user_id 更新；该用户首次更新时创建进度记录。

- Read：按 user_id 查看进度。

- percentage 必须为 0–100。

- user_id 和 progress.id 是两个字段，API 不混用。

- 不存在的用户 → 404；没有进度记录 → 404。

## Model Gateway 模型网关

- 接收 prompt + context，返回 model_output。

- 当前为本地模拟回复，没有连接外部 AI API。

- 生成结果是草稿；修改后点击保存，才写入学习计划。

# 2. Project Structure

```text

backend/

  main.py

  auth.py

  permissions.py

  database.py

  models.py

  model_gateway.py

  routes/

    users.py

    progress.py

    studyplan.py

    assign.py

  security/

    validation.py

    rate_limit.py

    errors.py

  utils/

    hashing.py

    tokens.py

frontend/

  index.html

  app.js

  style.css

tests/

  conftest.py

  test_auth.py

  test_permission.py

  test_rbac_assignment.py

  test_progress.py

  test_studyplan.py

  test_rate_limit.py

  test_model_gateway.py

  test_security.py

docs/

  architecture.md

  security_report.md

  testing_report.md

requirements.txt

week24.docx

```

# 3. Running the Backend

Python 3.10+，在项目根目录运行：

```powershell

python -m pip install -r requirements.txt

python -m uvicorn backend.main:app --reload

```

API 文档：http://127.0.0.1:8000/docs

SQLite 默认保存在 database/week24.db，启动时创建缺失的表。

现有数据保留。注册账号默认为 Student，已有 Teacher / Admin 可继续登录。

没有 Teacher / Admin 时，只能由项目维护者在本地数据库设置；注册接口不接受角色提升。

# 4. Running the Frontend

最简单方式：启动 Backend 后，直接访问 http://127.0.0.1:8000。

Backend 同时提供前端页面和 API。无需再开前端终端。

下面是单独运行前端的可选方式：

另开终端，在项目根目录运行：

```powershell

cd frontend

python -m http.server 3000

```

浏览器访问 http://localhost:3000，与 Backend CORS 配置一致。

1. 注册或登录。

2. Student 使用自己的 User ID；Teacher / Admin 输入目标学生的 User ID。

3. 更新 / 查看进度，保存 / 查看最新学习计划。

4. 调用模型生成草稿，再修改并保存。

5. Admin 可在 Teacher Assignment 中选择教师 / 学生；在 Users 页面更改角色和密码。

# 5. Running Tests

在项目根目录运行：

```powershell

python -m pytest -q

```

测试为每个用例创建独立的临时 SQLite 数据库，自动准备 Student / Teacher / Admin。

不依赖真实账号，不修改 database/week24.db。测试密码 123 仅用于临时测试数据。

# 6. API Overview

```text

POST /api/users/register

POST /api/users/login

POST /api/studyplan/{user_id}

GET  /api/studyplan/{user_id}

PUT  /api/progress/user/{user_id}

GET  /api/progress/user/{user_id}

POST /api/assign/{teacher_id}/{student_id}  # Admin only

POST /api/model/generate

```

登录后通过 token 请求头传递凭证。旧的 /api/progress/{id} 路径不再使用。

# 7. Security Summary

- Missing / invalid token → 401。

- 已登录但没有权限 → 403。

- Admin-only Assignment，重复分配不会重复插入。

- Backend 检查 Ownership 和 Teacher Assignment。

- 每个 token 每 60 秒最多 20 次请求，第 21 次 → 429。

- 缺少字段 / 类型不符 → 422；空计划 / 超长计划 / 越界进度 → 400。

- 模型是模拟实现，不能把输入长度检查当作内容安全检查。

当前是本地学习原型。Token 和限流状态保存在进程内，Backend 重启后需要重新登录。

页面退出只清除当前页面的登录状态；当前没有服务器端注销接口。

测试覆盖的具体范围见 docs/testing_report.md。
