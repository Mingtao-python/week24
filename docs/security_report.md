# Security Report — AI Learning Platform V2

## 1. Authentication

- Login 返回 token + user_id + role。
- authenticate() 通过 token 查用户，再从数据库读取角色。
- 缺少 / 无效 token → 401。
- Register 固定创建 Student。注册、登录无需 token。

## 2. Authorization

| Role | StudyPlan / Progress | Assignment |
|---|---|---|
| Student | 自己的数据 | 403 |
| Teacher | 已分配学生的数据 | 403 |
| Admin | 学习数据 | 200，需有效 Teacher / Student |

Assignment 先执行 require_role(user, ["admin"])，再访问数据库。
Teacher 无法把任意学生分配给自己。重复分配不新增重复关系。
页面隐藏 Admin 按钮不能代替后端检查。

## 3. Ownership

Progress 使用 /api/progress/user/{user_id}，按 user_id 检查权限和读写。
不会把 progress.id 当作 user_id。
不存在的用户更新返回 404，不会给当前用户偷偷创建资源。
输入验证失败不写入进度。

## 4. Validation

- 缺少必填字段 / 类型不符 → 422。
- 计划和模型 prompt 为空白或超过 1000 字符 → 400。
- percentage 不在 0–100 → 400。
- Assignment 用户不存在 → 404，角色不匹配 → 400。

长度检查不能证明模型输入或输出安全，当前没有专门的内容审核。

## 5. Rate Limit and Errors

- 单个 token 在 60 秒内最多 20 次请求。
- 第 21 次由 middleware 返回 429 JSON。
- 业务 HTTPException 返回明确状态和 detail。
- 未处理异常使用统一 500 消息。
- CORS 限制浏览器来源，权限仍由后端独立验证。

## 6. Current Limits

这是本地学习原型。Token 和限流记录保存在进程内，未实现过期、服务器端注销和多进程共享。
密码仍使用原有 SHA-256，尚未升级为带盐的密码哈希。
Model Gateway 是模拟回复，未接外部 API。
当前测试验证列出的行为，不代表生产环境安全审计。
