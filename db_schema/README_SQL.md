# Forensic Medico-Legal Database — SQL Scripts & Security Suite

This directory contains the organized PostgreSQL database scripts for the **Forensic Medico-Legal Database System**.

---

## 📂 File Directory & Execution Order

To set up or refresh the database from scratch, execute the SQL files in numerical order:

```bash
# 1. Create Tables, Primary/Foreign Keys & Indexes
psql -U postgres -d forensic_db -f 01_ddl_schema.sql

# 2. Insert Seed Data, System Roles, and Default Records
psql -U postgres -d forensic_db -f 02_dml_seed_data.sql

# 3. Create Analytical & Operational System Views
psql -U postgres -d forensic_db -f 03_views.sql

# 4. Create Audit Trail & Status Automation Triggers
psql -U postgres -d forensic_db -f 04_triggers_and_functions.sql

# 5. Create Stored Procedures & Business Logic Functions
psql -U postgres -d forensic_db -f 05_stored_procedures.sql

# 6. Apply Database Security, RBAC Roles & Row Auditing
psql -U postgres -d forensic_db -f 06_security_and_rbac.sql

# 7. Run Operational, Reporting & Diagnostic Queries
psql -U postgres -d forensic_db -f 07_queries.sql
```

---

## 📄 File Summaries

| Script File | Type | Description |
| :--- | :--- | :--- |
| **`01_ddl_schema.sql`** | **DDL** | Defines all 26 core tables, constraints, foreign key cascade actions, and B-Tree indexes across Security, People, Case Log, Examination Subtypes, Specimens, and Reports. |
| **`02_dml_seed_data.sql`** | **DML** | Inserts foundational seed data (roles, grievous hurt lookup codes), demo staff, app users, police stations, courts, patients, cases, examinations, lab requests, lab results, and audit logs. |
| **`03_views.sql`** | **Views** | Creates key system views: `v_case_summary`, `v_stats_by_type`, `v_pending_reports`, `v_event_overview`, `v_lab_chain_of_custody`, and `v_staff_workload`. |
| **`04_triggers_and_functions.sql`** | **Triggers** | Implements automated audit logging (`fn_audit_log_change`), status transition upon receiving lab results (`fn_update_case_status_on_lab_result`), and notification insertion on case assignment. |
| **`05_stored_procedures.sql`** | **Procedures** | Encapsulates complex workflows: `sp_register_case`, `sp_submit_lab_request`, and `sp_despatch_report`. |
| **`06_security_and_rbac.sql`** | **Security** | Configures PostgreSQL native Role-Based Access Control (`role_admin`, `role_jmo`, `role_clerk`, `role_tech_officer`), privilege grants/revokes, and `db_security_audit` table. |
| **`07_queries.sql`** | **Queries** | Provides ready-to-run queries for patient lookup, overdue lab request tracking, injury penal code analysis, monthly medico-legal statistics, and specimen chain-of-custody. |

---

## 🔒 Security Architecture

1. **Role-Based Access Control (RBAC)**:
   - `role_admin`: Manages application configuration, user accounts, and staff. Access to sensitive patient clinical details is explicitly revoked to enforce medical confidentiality.
   - `role_jmo`: Full access to medico-legal case records, examinations, injuries, and lab requests. Blocked from system administration and user management.
   - `role_tech_officer`: Access to specimen logs and lab results.
   - `role_clerk`: Read-only access to master case logs and patient intake creation. Blocked from detailed postmortem/clinical findings.

2. **Dual-Layer Auditing**:
   - **Application Audit Log** (`audit_log`): Tracks user activity at the web application level.
   - **Database Native Audit Log** (`db_security_audit`): Tracks direct database mutations via `fn_audit_trigger()`.
