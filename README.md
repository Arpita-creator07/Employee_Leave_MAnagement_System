# Employee-LeaveManagement-System

A Flask-based employee leave management application for submitting, tracking, and managing leave requests.

## What The App Does

This app supports two main user flows:

- Employees can register, log in, view their leave dashboard, update their profile, submit leave requests, attach supporting documents, and track request status.
- Admins can view dashboard metrics, manage pending leave requests, approve or reject requests with comments, view a leave calendar, add employees, and configure leave policy limits.

## Tech Stack

- Backend: Python, Flask
- Database: Microsoft SQL Server through `pyodbc`
- Configuration: `python-dotenv`
- Frontend: HTML, Jinja templates, CSS, Bootstrap, Tailwind CDN, vanilla JavaScript
- Local dev helper: npm scripts that run Flask

## Requirements

- Python 3.14 or compatible Python 3.x
- Microsoft SQL Server LocalDB or SQL Server
- ODBC Driver 17 or 18 for SQL Server
- Node.js/npm only if you want to use `npm run dev`

## Local Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Configure the database connection in `.env`.

Example for SQL Server LocalDB:

```env
SERVER=(localdb)\MSSQLLocalDB;
DATABASE=EmployeeLeaveManagementSystem;
Trusted_Connection=yes;
Encrypt=yes;
TrustServerCertificate=yes;
SECRET_KEY=change-this-secret-key
```

The app defaults to the `EmployeeLeaveManagementSystem` database name. Make sure the database exists and contains the expected `users` and `leaves` tables before logging in or submitting requests.

4. Run the app:

```powershell
npm run dev
```

Or run Flask directly:

```powershell
python -m flask --app app run --debug
```

5. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Useful Commands

Run a syntax check:

```powershell
python -m compileall app.py config.py database models routes utils
```

Start without debug mode:

```powershell
npm start
```

## Project Structure

```text
app.py                  Flask app entry point
config.py               Environment and database connection config
database/               Database connection helper
models/                 Data access functions
routes/                 Flask blueprints for auth, employee, and admin flows
templates/              HTML/Jinja pages
static/                 CSS, JavaScript, uploads, and static assets
requirements.txt        Python dependencies
package.json            npm scripts for local Flask commands
```
