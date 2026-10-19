# Architecture — AI Learning Platform V2

## 1. System

```text
Browser (http://localhost:3000)
↓ fetch + token
FastAPI (http://127.0.0.1:8000)
↓ Authentication
Permission (role + owner + teacher assignment)
↓ Validation
Model Gateway / SQLite
↓ JSON Response
Browser
```

Rate Limit 在 HTTP middleware 中按 token 计数。CORS 允许 http://localhost:3000。
注册和登录是公开入口，业务接口使用 authenticate 依赖。

## 2. Responsibilities

- frontend/：收集输入、展示结果、调用 API。不能决定最终权限。
- backend/auth.py：Token → 数据库用户，读取真实角色。
- backend/permissions.py：Student 访问自己，Teacher 访问已分配学生，Admin 访问学习数据。
- backend/routes/assign.py：Admin-only，验证 Teacher / Student 角色后保存关系。
- backend/routes/progress.py：以 user_id 查询和更新，首次更新创建该用户的进度。
- backend/routes/studyplan.py：创建计划，读取最近保存的计划。
- backend/model_gateway.py：本地模拟模型，接收 prompt + context，返回文本。
- backend/database.py：初始化 SQLite 表和连接。

## 3. Data

| Table | Fields | Use |
|---|---|---|
| users | id, username, password, role | 身份和角色 |
| progress | id, user_id, percentage | 学生进度 |
| studyplan | id, user_id, content | 学习计划记录 |
| teacher_students | id, teacher_id, student_id | 教师分配关系 |

progress.id 是记录编号，progress.user_id 是用户编号。
Frontend / API 使用 /api/progress/user/{user_id}，SQL 使用 WHERE user_id=?。
GET 不存在的进度返回 404。PUT 先验证权限、输入和用户存在，再创建或更新。

## 4. Model Path

```text
Frontend prompt
→ POST /api/model/generate
→ Authentication + Validation
→ call_model(prompt, context)
→ model_output
→ Frontend 草稿
→ 用户确认后 POST /api/studyplan/{user_id}
→ SQLite
```

生成与保存是两个明确动作。当前模型不会直接读写数据库。
没有实现外部模型调用、自动保存或模型内容安全审核。

## 5. Runtime

- 数据库路径以项目目录为基准，不依赖终端当前目录。
- Token 和 Rate Limit 使用进程内字典，当前按单进程原型运行。
- 测试使用临时数据库，和真实学习数据分开。
- 用户密码沿用当前项目的 SHA-256 实现；本项目仍是学习原型。
