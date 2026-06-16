const API = "http://127.0.0.1:5000";

document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (data.role === "admin") {
        location.href = "admin_dashboard.html";
    } else {
        location.href = "employee_dashboard.html";
    }
});
