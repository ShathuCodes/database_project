# Forensic Medico-Legal Database System

A complete database-backed web application for a Forensic Medicine Department,
built to satisfy the Mini Project brief (see assignment PDF) and matching the
supplied ER diagram (`Forensic_Medico_Legal_Database_ER.pdf`).

## Stack
- **Database:** PostgreSQL (schema in `db_schema/schema.sql`)
- **Backend:** Python Flask (raw SQL via `psycopg2`, no ORM — for transparent SQL in your report)
- **Auth:** Flask-Login + bcrypt password hashing
- **Frontend:** Server-rendered Jinja2 templates + Bootstrap 5

## Database Design

The schema directly implements the ER diagram's five sections:

1. **Security & Administration** — `role`, `app_user`, `audit_log`, `notification`
2. **People & Organisations** — `patient`, `police_station`, `investigating_officer`, `court`, `magistrate`, `staff`
3. **Case Master Log** — `case_master`, `case_assignment` (M:N), `inquest_verdict`
4. **Case Events & Medical Subtypes** — `case_event` (supertype) with three
   mutually-exclusive subtypes sharing its primary key: `clinical_examination`,
   `postmortem`, `skeletal_examination`; plus `injury`, `grievous_hurt_type`
   (lookup), `sexual_assault_finding`, `postmortem_organ_finding`,
   `body_identifier`, `skeletal_item`
5. **Specimens & Laboratory Chain** — `specimen`, `lab_request`,
   `lab_request_organ_tissue`, `lab_result`
6. **Reports** — `report`

All foreign keys, `CHECK` constraints (for enumerated values), `UNIQUE`
constraints, and indexes are defined in `schema.sql`. Reporting views
(`v_case_summary`, `v_stats_by_type`, `v_pending_reports`, `v_event_overview`)
are included for your "Queries & Reports" section.

`db_schema/seed.sql` contains realistic dummy data across **every** table
(patients, cases of all five case types, all three event subtypes, injuries,
specimens, lab requests/results, reports, audit log entries, notifications)
so the system is demoable immediately after setup.

## Setup

```bash
# 1. Create a PostgreSQL database
createdb forensic_db

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env with your DB credentials

# 4. Create schema + load seed data (also generates real bcrypt hashes)
export FLASK_APP=run.py
flask init-db

# 5. Run the app
python run.py
# visit http://127.0.0.1:5000
```

## Demo Logins
All seeded accounts use the password **`password123`**.

| Username       | Role            |
|----------------|-----------------|
| admin          | Administrator   |
| dr.perera      | Senior JMO      |
| dr.fernando    | JMO             |
| dr.silva       | JMO             |
| tech.wick      | Lab Technician  |
| clerk.rana     | Clerk           |

New accounts can also self-register from the login page (JMO / Senior JMO /
Lab Technician / Clerk).

## Role-Based Access
- **Administrator** — full access, plus Staff and User Account management
- **Senior JMO / JMO** — patients, cases, clinical/postmortem/skeletal
  examinations, specimens, lab requests, reports
- **Lab Technician** — specimens, lab requests & results
- **Clerk** — view patients/cases, view reports

## Project Structure
```
db_schema/
  schema.sql   -- full DDL matching the ER diagram
  seed.sql     -- dummy data for every table
app/
  __init__.py, config.py, database.py, models.py, helpers.py
  routes/      -- one blueprint per module (auth, dashboard, patients,
                  cases, clinical, postmortem, skeletal, evidence, lab,
                  reports, staff, users)
  templates/   -- Jinja2 + Bootstrap 5 views, one folder per module
run.py         -- app entrypoint + `flask init-db` CLI command
```

## Mapping to the Assignment Brief
| Assignment Module        | Implementation                              |
|---------------------------|---------------------------------------------|
| Patient Management        | `patients` blueprint                         |
| Case Management            | `cases` blueprint                            |
| Postmortem Management       | `postmortem` blueprint (+ `clinical`, `skeletal`) |
| Evidence Management          | `evidence` (specimens) + `lab` blueprints    |
| Court Report Management        | `reports` blueprint                          |
| Staff Management                 | `staff` blueprint                            |
| User Authentication & Security    | `auth` blueprint, `role`/`app_user`, `audit_log` |
| Report Generation                   | Dashboard charts + `v_*` SQL views           |

Additional features already wired in: audit logging on every write,
in-app notifications table, role-based access control, chain-of-custody
tracking for specimens, and grievous-hurt clause lookups (Penal Code s.311).
