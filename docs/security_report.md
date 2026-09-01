# Security Report — AI Learning Platform V2

AI Learning Platform V2 implements a complete, multi-layered security system designed to protect user data, enforce permissions, validate input, prevent abuse, and ensure safe model interactions.  
This document explains the full security chain and how each layer works.

---

# 1. Security Chain Overview

Every request in the system passes through the following layers:
```
CORS
↓
Rate Limit Middleware
↓
Authentication (token → user)
↓
Authorization (RBAC + ownership + teacher assignment)
↓
Validation (schema + custom rules)
↓
Business Logic (DB / Model Gateway)
↓
Error Handling (safe JSON)
↓
Response
```

This chain ensures that *no request can bypass security*, even if the route is misconfigured.

---

# 2. Authentication

Implemented in `backend/auth.py`.

### Mechanism
- Token-based authentication.
- User logs in via `/api/users/login`.
- Backend returns:
  - `token`
  - `user_id`
  - `role`

### Security Rules
- Missing token → `401 Unauthorized`
- Invalid token → `401 Unauthorized`
- Token maps to a user in the database.

### Why it matters
Authentication ensures that every request is tied to a real user identity.

---

# 3. Authorization (RBAC + Ownership + Teacher Assignment)

Implemented in `backend/permissions.py`.

### Role Matrix

| Role     | Allowed Actions |
|----------|-----------------|
| student  | Only own resources |
| teacher  | Only assigned students |
| admin    | Full access |

### Ownership Enforcement
Students can only access their own:

- progress  
- studyplan  

If a student tries to access another student's resource → `403 Forbidden`.

### Teacher Assignment
Teachers must be explicitly assigned to students:

```
POST /api/assign/{teacher_id}/{student_id}
```

If a teacher tries to access a non-assigned student → `403 Forbidden`.

### Admin
Admin bypasses all checks.

### Why it matters
Authorization prevents horizontal privilege escalation and ensures strict resource isolation.

---

# 4. Input Validation

Implemented in `backend/security/validation.py`.

### Validation Rules
- Empty input → `400 Bad Request`
- Input longer than 1000 chars → `400 Bad Request`
- Progress percentage must be 0–100 → `400 Bad Request`

### Validation Applied To
- Model Gateway (`/api/model/generate`)
- StudyPlan creation
- Progress update

### Why it matters
Validation prevents malformed input, prompt injection attempts, and accidental misuse.

---

# 5. Rate Limiting

Implemented in `backend/security/rate_limit.py`.

### Rules
- Each token can make **20 requests per minute**.
- The **21st request** returns:
```
429 Too Many Requests
```

### Why it matters
Rate limiting prevents:

- Abuse  
- Infinite loops  
- Scripted attacks  
- Model spamming  

---

# 6. Error Handling

Implemented in `backend/security/errors.py`.

### Handled Exceptions
- `HTTPException` → returns status + detail
- `ValidationError` → returns `400 Invalid input format`
- Generic `Exception` → returns `500 Internal server error`

### Security Benefits
- No stack traces leak to the client  
- No internal error messages  
- All errors return safe JSON  
- Prevents information disclosure  

---

# 7. Model Gateway Security

Model Gateway (`/api/model/generate`) is protected by:

### ✔ Authentication  
Token required.

### ✔ Authorization  
Can be extended to role-based model access.

### ✔ Validation  
Prompt must be non-empty and safe.

### ✔ Rate Limit  
Model calls count toward the 20/min limit.

### ✔ Error Handling  
All model errors return safe JSON.

### Why it matters
Model Gateway is often the most sensitive part of an AI system.  
This design ensures it cannot be abused or exploited.

---

# 8. Teacher–Student Assignment Security

Teacher assignment is stored in:

```
teacher_students (teacher_id, student_id)
```

Security rules:

- Only admin can assign students.
- Teacher can only access assigned students.
- Students cannot assign themselves.

This prevents unauthorized access to student data.

---

# 9. Summary

AI Learning Platform V2 implements a complete, production-grade security system:

- ✔ Authentication  
- ✔ Authorization (RBAC + ownership + teacher assignment)  
- ✔ Input validation  
- ✔ Rate limiting  
- ✔ Safe error handling  
- ✔ Secure model gateway  
- ✔ Full test coverage  

This security architecture fully satisfies Week24 Product requirements and ensures the system is safe, robust, and ready for deployment.