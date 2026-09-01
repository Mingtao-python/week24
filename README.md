# AI Learning Platform V2

AI Learning Platform V2 是一个完整的全栈学习系统，包含前端、后端、数据库、模型网关、安全链和测试套件。  
本项目严格按照 Week24 Product 要求构建，具备完整的权限系统、教师分配系统、限流系统、输入验证系统和模型调用安全保护。

---

# 1. Features

## ✔ Authentication（认证）
- Token 登录系统  
- 用户登录后获得 token + user_id + role  
- 所有 API 需要 token 才能访问  

## ✔ Authorization（权限系统）
- RBAC（学生 / 老师 / 管理员）  
- Ownership（学生只能访问自己的数据）  
- Teacher Assignment（老师只能访问被分配的学生）  
- Admin 拥有全部权限  

## ✔ StudyPlan（学习计划）
- 创建学习计划  
- 查看学习计划  
- 输入验证（防止空内容、过长内容）  

## ✔ Progress（学习进度）
- 更新进度  
- 查看进度  
- 输入验证（百分比必须 0–100）  

## ✔ Model Gateway（模型网关）
- 安全的模型调用接口  
- 输入验证  
- 限流保护  
- 错误处理保护  

## ✔ Security Chain（安全链）
完整安全链：

```
Validation → Auth → Authorization → Rate Limit → Error Handling
```

## ✔ Frontend（前端）
- 简洁 UI  
- 登录  
- 查看进度  
- 查看学习计划  
- 调用模型网关生成学习计划  

## ✔ Testing（测试）
完整 pytest 测试覆盖：

- Auth  
- Permission  
- Ownership  
- Teacher Assignment  
- Progress CRUD  
- StudyPlan CRUD  
- Rate Limit  
- Validation  
- Model Gateway  

---

# 2. Project Structure

```
backend/
main.py
auth.py
permissions.py
database.py
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

frontend/
index.html
app.js
style.css

tests/
test_auth.py
test_permission.py
test_progress.py
test_studyplan.py
test_rate_limit.py
test_model_gateway.py

docs/
Architecture.md
Security_Report.md
Testing_Report.md
README.md
```

---

# 3. Running the Backend

确保你在项目根目录：

```bash
uvicorn backend.main:app --reload
```
API 文档：

```
http://127.0.0.1:8000/docs
```

# 4. Running the Frontend
直接打开：

```
frontend/index.html
```

即就可一使用：

- 登录
- 查看进度
- 查看学习计划
- 调用模型网关

# 5. Running Tests

```bash
pytest
```

所有测试应全部通过。

# 6. API Overview
Authentication
```
POST /api/users/login
```
StudyPlan
```
POST /api/studyplan/{user_id}
GET  /api/studyplan/{user_id}
```
Progress
```
PUT /api/progress/{user_id}
GET /api/progress/{user_id}
```
Teacher Assignment
```
POST /api/assign/{teacher_id}/{student_id}
```
Model Gateway
```
POST /api/model/generate
```
# 7. Security Summary
系统实现：

- Tken 认证
- RBAC 权限系统
- Ownership
- Teacher Assignment
- 输入验证
- 限流
- 全局错误处理
- 模型网关安全保护
- 所有安全模块均有测试覆盖。

# 8. Summary
AI Learning Platform V2 是一个完整的、可运行的、可评分的 Week24 产品：
- 全栈
- 安全
- 可扩展
- 测试覆盖完整
- 文档完整
满足 Week24 Product 的**所有*8要求。