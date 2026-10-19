# Testing Report — AI Learning Platform V2

## 1. Run

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

每个测试使用临时 SQLite 数据库，自动准备角色账号，清空 Token 和 Rate Limit 状态。
不读取或修改真实 database/week24.db。

## 2. Tests

| File | Checks |
|---|---|
| test_auth.py | Login 返回 token / user_id / role，错误密码 401，缺字段 422 |
| test_permission.py | Student 越权 403，未分配 Teacher 403 |
| test_rbac_assignment.py | Admin assign 200，Teacher / Student 403，No token 401，分配角色和账号检查，重复分配，Teacher / Admin 读取 |
| test_progress.py | 更新和读取，user_id 与记录 ID 不同，非法进度不写入，不存在用户 404，旧路径拒绝 |
| test_studyplan.py | 创建 / 读取，Student 越权，Teacher assigned / unassigned，Admin，输入验证，无 token，读取最新计划 |
| test_rate_limit.py | 已存在计划前 20 次读取 200，第 21 次 429 |
| test_model_gateway.py | No token 401，正常输入 200，空白输入 400 |
| test_security.py | 缺少字段 422，无 token 401 |

StudyPlan 实现 Create / Read，Progress 实现 Update / Read。
没有声明完整 Create / Read / Update / Delete，也没有声称已覆盖所有安全路径。

## 3. Frontend Check

Backend 启动后，在 frontend 目录运行 python -m http.server 3000。
访问 http://localhost:3000，检查：

1. 注册和登录。
2. 更新 / 读取自己的进度。
3. 生成模拟学习计划，修改后保存，再读取。
4. 改成其他学生编号，Student 收到 403。
5. Admin 分配后，Teacher 可读取该学生数据。

API pytest 测试不等同于真实浏览器端到端测试。


## 4. Verified Results

- 39 tests passed。
- 浏览器实测：Student 登录 → 更新进度 → 生成模拟草稿 → 保存计划 → 读取计划。
- Student 改成其他用户编号 → 403: Not your resource。
- 浏览器使用 http://localhost:3000，Backend 使用独立的临时测试数据库。
- Python 3.12；FastAPI 0.149.0；pytest 9.1.1；httpx 0.28.1。
- 依赖提示：Starlette 当前对 httpx TestClient 发出弃用警告；本次测试通过。


## Role management verification

- 51 pytest checks passed, using disposable databases.
- Teacher directory contains only assigned students. Unassigned student data returns 403.
- Teachers have read access; write and model-generation requests return 403.
- Only Admin can list all users, change roles, or reset passwords.
- Password reset rejects invalid lengths, changes login credentials, and revokes old tokens.
- Browser checks covered Student, Admin, assigned Teacher, and Teacher without students.
- Role controls are hidden as appropriate; empty Teacher views hide learning controls.
