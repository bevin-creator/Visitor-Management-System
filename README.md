# Visitor Management System

A secure web application for front-desk and security teams to register visitors, manage check-ins and check-outs and maintain an auditable record of site activity.

## Features

Authentication & Roles - JWT authentication with Admin, Manager and Guard roles.

Visitor Registration - Register visitors and check them in from one form.

Visitor Tracking - View active visitors and manage check-outs.

Search - Search by name, email, phone or ID using encrypted data and blind indexes.

Dashboard - View daily and weekly visitor statistics.

Reports - Generate date-range reports and export visitor records as PDFs.

User Management - Admins can create users and assign roles.

Audit Logging - Records important activities such as logins, registrations, check-ins, check-outs and deletions.

ID Verification - Optional integration with an external ID verification provider.

## Security

The system is designed with privacy and security in mind:

- Sensitive visitor information is encrypted before being stored.
- Phone and ID numbers use blind indexes to support exact searches without storing searchable plaintext.
- Role-based access control (RBAC) limits access according to user responsibilities.
- ID numbers are masked based on the user's role.
- Important system activities are recorded through audit logging.
- JWT-based authentication protects API endpoints.

## Tech Stack

| Component        | Technology            |
| ---------------- | --------------------- |
| Frontend         | HTML, CSS, JavaScript |
| Backend          | FastAPI / Python      |
| Database (local)        | SQLite            |
| Database   | PostgreSQL              |
| Authentication   | JWT                   |
| Password Hashing | bcrypt                |
| Encryption       | AES-256-CBC + HMAC    |
| Backend Hosting  | Render                |
| Frontend Hosting | Vercel                |

## User Roles

### Admin

- Full system access
- Manage users and roles
- Manage visitor records
- View complete ID numbers
- Delete visitor records

### Manager

- Manage visitors
- View reports
- View partially masked ID numbers

### Guard

- Register visitors
- Check visitors in and out
- View visitor information required for front-desk operations

## Live Demo

[Visitor Management System](https://visitor-management-system-psi-one.vercel.app/login.html)

## Running Locally

### Requirements

- Python 3.12
- A modern web browser
- PostgreSQL (optional — SQLite can be used locally)

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# Windows
copy .env.example .env

# macOS/Linux
# cp .env.example .env

uvicorn app.main:app --reload --port 8000
```

The database tables are created automatically when the application starts.

### Create the First Admin

Add the following to `.env` before starting the backend:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
ADMIN_EMAIL=admin@example.com
```

The application creates the initial admin account automatically if one does not already exist.

### Frontend

Open:

```text
frontend/login.html
```

directly in a browser

The FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

## Configuration

Configuration is managed through environment variables. See `.env.example` for the complete list.

Important variables include:

```env
DATABASE_URL=
SECRET_KEY=
ENCRYPTION_KEY=
CORS_ORIGINS=

ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_EMAIL=

ID_VERIFICATION_API_URL=
```

`ID_VERIFICATION_API_URL` can be left empty to disable external ID verification.

## Privacy & Data Protection

Visitor phone numbers and ID numbers are encrypted before being stored in the database. Searchable fields use keyed blind indexes, allowing exact lookups without exposing the original plaintext values.

ID numbers are also protected through role-based masking:

Admin: Full ID number
Manager: Last four digits
Guard: ID number hidden

## Project Purpose

The system provides a digital alternative to manual visitor logbooks while improving security, accountability, privacy and visitor tracking.

## Testing

The backend includes automated tests using **pytest** for authentication, RBAC, encryption, visitor management, blind-index search, check-in/check-out workflows, reporting, audit logging, and security regression cases.

### Run the Tests

From the `backend` directory:

```bash
pip install -r requirements.txt
pip install pytest
pytest -v
```

For a summary including expected failures:

```bash
pytest -ra
```

To run a specific test file:

```bash
pytest -v tests/test_visitors.py
```

The test suite is located in:

```text
backend/tests/
```

and includes:

```text
test_database.py
test_encryption.py
test_auth.py
test_user_management.py
test_rbac.py
test_visitors.py
test_workflow.py
test_reports_dashboard_audit.py
test_security_regressions.py
```

Tests marked **XFAIL** represent known security or implementation limitations that are intentionally retained as regression tests.

The tests use an isolated SQLite test database configured in `tests/conftest.py` and do not require the development PostgreSQL database.