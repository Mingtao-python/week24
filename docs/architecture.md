# Architecture — AI Learning Platform V2

## 1. Overview

AI Learning Platform V2 是一个完整的全栈学习系统，包含：

- 前端（HTML + JavaScript）
- 后端（FastAPI）
- 数据库（SQLite）
- 模型网关（Model Gateway）
- 权限系统（RBAC + Ownership + Teacher Assignment）
- 安全链（Validation → Auth → Authorization → Rate Limit → Error Handling）
- 测试套件（pytest）

系统目标：  
为学生、老师、管理员提供一个安全、可扩展、可验证的学习平台。

---

## 2. System Architecture Diagram

```
Browser (Frontend)
↓
FastAPI (Backend)
↓
Authentication (token → user)
↓
Authorization (role + ownership + teacher assignment)
↓
Validation (input schema + custom rules)
↓
Rate Limit (per-token)
↓
Model Gateway / Database
↓
Error Handling (safe JSON)
↓
Response
```

---

## 3. Backend Structure

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
```

---

## 4. Frontend Structure

```
frontend/
index.html
app.js
style.css
```

前端通过 fetch 调用后端 API，实现：

- 登录  
- 查看进度  
- 查看学习计划  
- 调用模型网关生成学习计划  

---

## 5. Database Schema

### users
| id | username | password | role |
|----|----------|----------|------|
| PK | TEXT     | TEXT     | student/teacher/admin |

### progress
| id | user_id | percentage |
|----|---------|------------|

### studyplan
| id | user_id | content |
|----|---------|---------|

### teacher_students
| id | teacher_id | student_id |
|----|------------|------------|

---

## 6. Model Gateway

模型网关统一管理所有模型调用：

```python
def call_model(prompt, context):
    if "study plan" in prompt.lower():
        return "Weekly Study Plan: 1) Review notes 2) Practice problems 3) Take a quiz."
    return "Model response placeholder."
```
它被保护在：
- Authentication
- Validation
- Rate Limit
- Error Handling
之后。

## 7. Security Chain
完整安全链：
```
CORS
↓
Rate Limit Middleware
↓
Authentication
↓
Authorization
↓
Validation
↓
Business Logic (DB / Model)
↓
Error Handling
↓
Response
```
## 8. Summary
本架构满足 Week24 Product 所有要求：
- 全栈系统
- 完整权限系统
- 安全链
- 模型网关
- 前端 UI
- 测试覆盖
- 文档完整
这是一个可运行、可扩展、可评分的完整学习平台系统。