//只剩非常集中的收尾：
//frontend/app.js
///api/progress/${userId}
//改成
///api/progress/user/${userId}
//tests/test_progress.py同样改成新路径。
//运行完整：
//python -m pytest -q
//确认不是只“写了测试”，而是真正全部PASS。
//更新docs/testing_report.md，把新增测试和真实结果写进去。
//完成这4个小收尾后，Week24 Product从目前源码状态看，就基本可以冻结交付了。

//My comment: this was aready done in the previus commit(line 234 in this version).
const API = location.port === "3000" ? "http://127.0.0.1:8000" : location.origin;
let session = null;
let students = [];
let users = [];
const byId = (id) => document.getElementById(id);
function showStatus(message) { byId("status").textContent = message; }
async function request(path, method = "GET", body = null) {
  const headers = {};
  if (session) headers.token = session.token;
  if (body !== null) headers["Content-Type"] = "application/json";
  const response = await fetch(API + path, {
    method,
    headers,
    body: body === null ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    const message = typeof data.detail === "string" ? data.detail : "Request failed";
    if (response.status === 401 && session) clearSession();
    throw new Error(`${response.status}: ${message}`);
  }
  return data;
}
async function run(action) {
  showStatus("Loading...");
  try {
    await action();
    if (byId("status").textContent === "Loading...") showStatus("Done 完成");
  } catch (error) {
    showStatus(error.message);
  }
}
function fillSelect(select, rows, label) {
  select.replaceChildren();
  for (const row of rows) {
    const option = document.createElement("option");
    option.value = row.id;
    option.textContent = label(row);
    select.append(option);
  }
}
function selectedStudentId() {
  if (session.role === "student") return session.user_id;
  const id = Number(byId("student-id").value);
  if (!Number.isInteger(id) || id < 1) throw new Error("Choose a student first");
  return id;
}
function clearLearning() {
  const prompt = session?.role === "student" ? "Click Read to view your saved data." : "Choose a student and click Read.";
  byId("progress-value").textContent = prompt;
  byId("plan-value").textContent = prompt;
  byId("percentage").value = "";
  byId("plan-content").value = "";
  byId("model-output").textContent = "";
}
async function loadUsers() {
  users = await request("/api/users/");
  students = users.filter((user) => user.role === "student");
  fillSelect(byId("student-id"), students, (user) => `${user.username} (ID ${user.id})`);
  fillSelect(byId("teacher-id"), users.filter((user) => user.role === "teacher"), (user) => `${user.username} (ID ${user.id})`);
  fillSelect(byId("assigned-student-id"), students, (user) => `${user.username} (ID ${user.id})`);
  byId("learning-panel").hidden = students.length === 0;
  clearLearning();
  renderUsers();
}
async function loadTeacherStudents() {
  students = await request("/api/users/teacher/students");
  fillSelect(byId("student-id"), students, (user) => `${user.username} (ID ${user.id})`);
  byId("teacher-empty").hidden = students.length > 0;
  byId("student-picker").hidden = students.length === 0;
  byId("learning-panel").hidden = students.length === 0;
  clearLearning();
  byId("teacher-students").replaceChildren();
  for (const user of students) {
    const item = document.createElement("li");
    item.textContent = `${user.username} (ID ${user.id})`;
    byId("teacher-students").append(item);
  }
}
function renderUsers() {
  const list = byId("users-list");
  list.replaceChildren();
  const table = document.createElement("table");
  const head = document.createElement("tr");
  for (const title of ["ID", "Username", "Role", "Change role", "New password"]) {
    const th = document.createElement("th");
    th.textContent = title;
    head.append(th);
  }
  table.append(head);
  for (const user of users) {
    const row = document.createElement("tr");
    for (const value of [user.id, user.username, user.role]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    const roleCell = document.createElement("td");
    const role = document.createElement("select");
    for (const value of ["student", "teacher", "admin"]) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      option.selected = value === user.role;
      role.append(option);
    }
    const saveRole = document.createElement("button");
    saveRole.textContent = "Save";
    saveRole.addEventListener("click", () => run(async () => {
      await request(`/api/users/${user.id}/role`, "PUT", { role: role.value });
      if (user.id === session.user_id && role.value !== "admin") {
        byId("logout").click();
        showStatus("Your role changed. Please sign in again.");
        return;
      }
      await loadUsers();
    }));
    roleCell.append(role, saveRole);
    row.append(roleCell);
    const passwordCell = document.createElement("td");
    const password = document.createElement("input");
    password.type = "password";
    password.minLength = 8;
    password.maxLength = 128;
    password.required = true;
    password.autocomplete = "new-password";
    password.placeholder = "At least 8 characters";
    password.setAttribute("aria-label", `New password for ${user.username}`);
    const reset = document.createElement("button");
    reset.textContent = "Reset";
    reset.addEventListener("click", () => run(async () => {
      if (!password.reportValidity()) throw new Error("Use a password of 8–128 characters.");
      await request(`/api/users/${user.id}/password`, "PUT", { password: password.value });
      password.value = "";
      if (user.id === session.user_id) {
        byId("logout").click();
        showStatus("Password changed. Sign in again with the new password.");
        return;
      }
      showStatus(`Password reset for ${user.username}. They must log in again.`);
    }));
    passwordCell.append(password, reset);
    row.append(passwordCell);
    table.append(row);
  }
  list.append(table);
}
function showRolePanels() {
  const role = session.role;
  byId("login-panel").hidden = false;
  byId("login-form").hidden = true;
  byId("logout").hidden = false;
  byId("identity").textContent = `${session.username} · ${role} · ID ${session.user_id}`;
  byId("student-picker").hidden = role === "student";
  byId("teacher-panel").hidden = role !== "teacher";
  byId("admin-panel").hidden = role !== "admin";
  byId("assignment-panel").hidden = role !== "admin";
  byId("learning-panel").hidden = false;
  byId("progress-form").hidden = !["student", "admin"].includes(role);
  byId("plan-form").hidden = !["student", "admin"].includes(role);
  byId("model-panel").hidden = !["student", "admin"].includes(role);
  byId("student-label").textContent = role === "teacher" ? "My assigned students 我的学生" : "Student 学生";
}
byId("login-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    const credentials = { username: byId("username").value, password: byId("password").value };
    clearSession();
    session = await request("/api/users/login", "POST", credentials);
    byId("password").value = "";
    showRolePanels();
    clearLearning();
    if (session.role === "admin") await loadUsers();
    if (session.role === "teacher") await loadTeacherStudents();
    if (session.role === "student") {
      byId("student-id").replaceChildren();
      const option = document.createElement("option");
      option.value = session.user_id;
      option.textContent = session.username;
      byId("student-id").append(option);
    }
  });
});
byId("register").addEventListener("click", () => run(async () => {
  if (!byId("login-form").reportValidity()) throw new Error("Enter username and password");
  await request("/api/users/register", "POST", {
    username: byId("username").value,
    password: byId("password").value,
  });
  byId("password").value = "";
  showStatus("Student account created. Please log in.");
}));
function clearSession() {
  session = null;
  students = [];
  users = [];
  byId("login-form").reset();
  byId("login-form").hidden = false;
  for (const id of ["teacher-panel", "admin-panel", "assignment-panel", "learning-panel", "student-picker"]) byId(id).hidden = true;
  byId("logout").hidden = true;
  byId("identity").textContent = "请登录 / Sign in";
  byId("users-list").replaceChildren();
  byId("teacher-students").replaceChildren();
  clearLearning();
}
byId("logout").addEventListener("click", () => { clearSession(); showStatus("Logged out"); });
byId("refresh-students").addEventListener("click", () => run(loadTeacherStudents));
byId("student-id").addEventListener("change", clearLearning);
byId("assign-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    await request(`/api/assign/${byId("teacher-id").value}/${byId("assigned-student-id").value}`, "POST");
    showStatus("Student assigned to teacher");
  });
});
byId("progress-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    const id = selectedStudentId();
    const percentage = Number(byId("percentage").value);
    await request(`/api/progress/user/${id}`, "PUT", { percentage });
    byId("progress-value").textContent = `Progress: ${percentage}%`;
  });
});
byId("read-progress").addEventListener("click", () => run(async () => {
  const data = await request(`/api/progress/user/${selectedStudentId()}`);
  byId("progress-value").textContent = `Progress: ${data.percentage}%`;
  if (session.role !== "teacher") byId("percentage").value = data.percentage;
}));
byId("plan-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    const content = byId("plan-content").value;
    await request(`/api/studyplan/${selectedStudentId()}`, "POST", { content });
    byId("plan-value").textContent = content;
  });
});
byId("read-plan").addEventListener("click", () => run(async () => {
  const data = await request(`/api/studyplan/${selectedStudentId()}`);
  byId("plan-value").textContent = data.studyplan;
  if (session.role !== "teacher") byId("plan-content").value = data.studyplan;
}));
byId("model-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    const data = await request("/api/model/generate", "POST", { prompt: byId("prompt").value, context: {} });
    byId("model-output").textContent = data.model_output;
    byId("plan-content").value = data.model_output;
  });
});
