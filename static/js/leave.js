const API = "http://127.0.0.1:5000";

const userId = localStorage.getItem("user_id");

async function applyLeave() {
    const type = document.getElementById("leave_type").value;
    const start = document.getElementById("start_date").value;
    const end = document.getElementById("end_date").value;
    const reason = document.getElementById("reason").value;

    const res = await fetch(`${API}/apply_leave`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            user_id: userId,
            leave_type: type,
            start_date: start,
            end_date: end,
            reason: reason,
        }),
    });

    const data = await res.json();
    alert(data.message);

    window.location.href = "employee_dashboard.html";
}
