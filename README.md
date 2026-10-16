# Software Bug Tracking and Issue Management System

A lightweight web application for recording and managing software defects. Users can create bug reports, set severity, assign issues, search records, and track status through a simple dashboard.

## Features
- Create and view bug reports
- Severity levels: Critical, High, Medium, Low
- Status workflow: Open, In Progress, Resolved
- Assign or reassign an issue
- Search by title, description, or assignee
- Filter issues by status
- Dashboard counts for total, open, in-progress, and resolved issues
- Input validation and safe parameterized SQL queries
- Automated tests with pytest

## Technology Stack
- Python
- Flask
- SQLite
- pytest
- HTML and CSS
- Git and GitHub

## Run Locally

Requires Python 3.10 or newer.

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run the commands without activation:
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in your browser.

## Run Tests
```powershell
python -m pytest -v
```

Or without activating the environment:
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Project Structure
```text
software-bug-tracking-system/
├── app.py
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py
```

## Scope and Limitations
This is an educational local demo. It does not implement user authentication or production security controls and should not be used with sensitive production data. The assignment field is a name field rather than a managed user account.

## Future Improvements
- User authentication and role-based permissions
- Edit bug descriptions and severity
- Pagination and exportable reports
- CI workflow for automatic test execution
