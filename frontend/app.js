let token = null;
let userId = null;

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch("http://127.0.0.1:8000/api/users/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const data = await res.json();

    if (res.status === 200) {
        token = data.token;
        userId = data.user_id;
        document.getElementById("login-status").innerText = "Login successful!";
        document.getElementById("actions").style.display = "block";
    } else {
        document.getElementById("login-status").innerText = "Login failed: " + data.detail;
    }
}

async function viewProgress() {
    const res = await fetch(`http://127.0.0.1:8000/api/progress/${userId}`, {
        headers: {"token": token}
    });

    const data = await res.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}

async function viewStudyPlan() {
    const res = await fetch(`http://127.0.0.1:8000/api/studyplan/${userId}`, {
        headers: {"token": token}
    });

    const data = await res.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}

async function generateStudyPlan() {
    const res = await fetch("http://127.0.0.1:8000/api/model/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "token": token
        },
        body: JSON.stringify({
            prompt: "Generate a study plan for me",
            context: {}
        })
    });

    const data = await res.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}
