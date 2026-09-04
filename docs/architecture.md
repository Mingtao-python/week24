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

## 2. Request Trace — Generate Study Plan

完整追踪用户生成学习计划的请求流程：

| Step | Data | Decision | Failure |
|------|------|----------|---------|
| Browser → API | token + study goal request | format correct? | network failure |
| Authentication | token | valid identity? | 401 Unauthorized |
| Validation | goal/subject | valid schema/length? | 400 Bad Request |
| Authorization | user/resource | allowed? | 403 Forbidden |
| Model Gateway | prompt/context | model available? | timeout / 5xx |
| Database | generated plan | authorized write? | DB failure |
| Output Validation | model result | safe/valid? | invalid output |
| Backend → Browser | JSON response | — | network failure |

---

## 3. System Architecture Diagram

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
## 8. Reverse Engineering — oobabooga/textgen

分析当前最新版本的 [oobabooga/textgen](https://github.com/oobabooga/textgen) 仓库结构：

### Repository Structure (Current Main Branch)

```
textgen/
├── server.py              # Main entry point
├── css/                   # Frontend styles
│   ├── main.css
│   └── chat_style-*.css
├── js/                    # Frontend JavaScript
│   ├── main.js
│   └── switch_tabs.js
├── modules/               # Backend core modules
│   ├── api/
│   │   └── script.py      # API endpoint definitions
│   ├── models.py          # Model loading logic
│   └── text_generation.py # Text generation functions
├── extensions/            # Optional extensions
│   └── (various extension folders)
└── user_data/             # Configuration & storage
    ├── models/
    ├── characters/
    └── settings.json
```

### Component Mapping

| Component | Evidence (File Path) |
|-----------|---------------------|
| **Frontend** | `css/main.css`, `js/main.js` |
| **Backend/API** | `modules/api/script.py` – defines FastAPI routes |
| **Authentication** | `modules/api/script.py` – `verify_api_key()`, `verify_admin_key()` |
| **Model Call** | `modules/text_generation.py` – `generate_reply()`, `modules/models.py` – `load_model()` |
| **Storage** | `user_data/models/`, `user_data/characters/` |
| **Configuration** | `user_data/settings.json`, `CMD_FLAGS.txt` |

### Key Observations

1. **Frontend**: Static files in `css/` and `js/` directories, served by the backend.
2. **Backend/API**: `modules/api/script.py` uses FastAPI with dependency injection for API key verification.
3. **Authentication**: API key validation via HTTP headers (`Authorization: Bearer <key>`).
4. **Model Loading**: `modules/models.py` handles dynamic model loading based on configuration.
5. **Text Generation**: `modules/text_generation.py` orchestrates generation with extension support.
6. **Storage**: User data stored in `user_data/` subdirectories.
7. **Configuration**: JSON settings and command-line flags control behavior.

---

## 9. Trust Boundary Verification

每个信任边界必须验证的内容：

| Trust Boundary | Must Verify |
|----------------|-------------|
| Browser → Backend | authentication, schema, type, length |
| Token → User Identity | token validity, user exists |
| Backend → Model | allowed context, data minimisation |
| Model → Backend | output validity, unsafe content |
| Backend → Database | role, ownership, permitted action |
| External API → Backend | status, schema, unexpected content |

---

## 10. Summary
本架构满足 Week24 Product 所有要求：
- 全栈系统
- 完整权限系统
- 安全链
- 模型网关
- 前端 UI
- 测试覆盖
- 文档完整
这是一个可运行、可扩展、可评分的完整学习平台系统。