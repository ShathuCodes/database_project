# Forensic Medico-Legal Database System

A database-backed web application for a Forensic Medicine Department, built matching the ER diagram and business rules.

---

## 🛠️ Technology Stack
- **Database:** PostgreSQL (raw SQL with views, stored procedures, triggers, RBAC security)
- **Backend:** Python Flask (raw SQL via `psycopg2`, no ORM for transparent SQL operations)
- **Authentication:** Flask-Login + bcrypt password hashing
- **Frontend:** Server-rendered Jinja2 templates + Bootstrap 5 + FontAwesome

---

## 🚀 How to Run

### 1. Prerequisites & Setup
Make sure PostgreSQL is running and you have Python installed.

Create virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Ensure your `.env` file in the root directory contains your PostgreSQL connection details:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=forensic_db
DB_USER=postgres
DB_PASSWORD=postgres
SECRET_KEY=forensic-secret-key
```

---

### 2. Initialize Database & Seed Data
To automatically create all tables, views, stored procedures, triggers, security rules, and seed demo accounts:

```bash
python run.py init-db
```
*(To do a complete wipe and rebuild at any time, run `python run.py init-db --force`)*

---

### 3. Run Option A: Web Application (Frontend + Backend)
To launch the web application server:

```bash
python run.py
```
1. Open your browser at **`http://127.0.0.1:5000`**
2. Log in with demo credentials below.

#### 🔑 Demo Accounts (Default Password: `password123`)
| Username       | Role            | Access Permissions |
|----------------|-----------------|--------------------|
| `admin`        | Administrator   | Full System Access & User/Staff Management |
| `dr.perera`    | Senior JMO      | Patients, Cases, Examinations, Reports |
| `dr.fernando`  | JMO             | Patients, Cases, Examinations, Reports |
| `tech.wick`    | Lab Technician  | Specimens, Lab Requests & Results |
| `clerk.rana`   | Clerk           | View Patients, Cases & Reports |

---

### 4. Run Option B: Backend Terminal Mode (Terminal Only)
If you want to query and inspect backend tables directly in the terminal without launching the web UI:

#### Run Database Inspector Script:
```bash
python view_tables.py
```

#### Run Custom 1-Line SQL Query:
```bash
python -c "import app.database as db; print(db.fetchall('SELECT patient_id, full_name, gender FROM patient LIMIT 5'))"
```

---

## 📂 Project Structure

```text
├── run.py                 # Application entrypoint & init-db CLI command
├── view_tables.py         # Terminal backend table inspector script
├── app/
│   ├── __init__.py        # App factory & Blueprint registration
│   ├── config.py          # Environment configuration loader
│   ├── database.py        # Raw PostgreSQL connection pool & SQL helper functions
│   ├── models.py          # User session loader model
│   ├── helpers.py         # Decorators for Role-Based Access Control (RBAC)
│   ├── routes/            # Modular backend route blueprints (auth, cases, patients, lab, etc.)
│   └── templates/         # Jinja2 HTML templates for Frontend
└── db_schema/             # Modular PostgreSQL Database Suite
    ├── 01_ddl_schema.sql             # DDL Tables, PK/FK Constraints & Indexes
    ├── 02_dml_seed_data.sql          # Seed Data for Demo & Testing
    ├── 03_views.sql                  # Analytical System Views
    ├── 04_triggers_and_functions.sql # Audit Log & Status Transition Triggers
    ├── 05_stored_procedures.sql      # Stored Procedures & Business Functions
    ├── 06_security_and_rbac.sql      # Database Security, Roles & Column Masking
    └── 07_queries.sql                # Operational Reporting Queries
```

---

## 🛡️ Database Architecture Highlights
1. **Security & Auditing:** Automated `audit_log` triggers record all `INSERT`, `UPDATE`, and `DELETE` operations along with user IDs and IP addresses.
2. **Status Automation:** Case status transitions (e.g., updating from `Awaiting Lab` to `Report Pending`) are triggered automatically upon lab result submission.
3. **Role-Based Access Control:** Dual-layer security enforced both in Flask routes (`@roles_required`) and PostgreSQL database permissions.
