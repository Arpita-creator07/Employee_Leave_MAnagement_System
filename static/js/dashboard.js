const API = "http://127.0.0.1:5000";

const userId = localStorage.getItem("user_id");

async function loadDashboard() {
    const res = await fetch(`${API}/dashboard/${userId}`);
    const data = await res.json();

    document.getElementById("total").innerText = data.total;
    document.getElementById("approved").innerText = data.approved;
    document.getElementById("rejected").innerText = data.rejected;
    document.getElementById("pending").innerText = data.pending;

    loadLeaves();
}

async function loadLeaves() {
    const res = await fetch(`${API}/my_leaves/${userId}`);
    const data = await res.json();

    const table = document.getElementById("leaveTable");
    table.innerHTML = "";

    data.leaves.forEach((leave) => {
        table.innerHTML += `
<tr onclick="showDetails('${leave.leave_type}', '${leave.start_date}', '${leave.end_date}', '${leave.status}', '${leave.reason}')">
    <td>${leave.leave_type}</td>
    <td>${leave.start_date}</td>
    <td>${leave.end_date}</td>
    <td>${leave.status}</td>
</tr>
`;
    });
}

function showDetails(type, start, end, status, reason) {
    document.getElementById("leaveType").innerText = type;
    document.getElementById("startDate").innerText = start;
    document.getElementById("endDate").innerText = end;
    document.getElementById("leaveStatus").innerText = status;
    document.getElementById("leaveReason").innerText = reason;

    const modal = new bootstrap.Modal(document.getElementById("leaveDetailsModal"));
    modal.show();
}

loadDashboard();
