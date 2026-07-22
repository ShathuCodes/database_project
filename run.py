from app import create_app
from app import database

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Create tables, views, triggers, stored procedures, security rules, and seed sample data."""
    import bcrypt
    from app import database

    conn = database.get_connection()
    cur  = conn.cursor()

    sql_files = [
        ('01_ddl_schema.sql', 'Creating DDL schema & indexes...'),
        ('02_dml_seed_data.sql', 'Seeding initial database records...'),
        ('03_views.sql', 'Creating analytical views...'),
        ('04_triggers_and_functions.sql', 'Creating audit & status triggers...'),
        ('05_stored_procedures.sql', 'Creating stored procedures...'),
        ('06_security_and_rbac.sql', 'Applying database-level security & RBAC...'),
    ]

    pw_hash = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode()

    for filename, msg in sql_files:
        print(msg)
        with open(f'db_schema/{filename}', 'r', encoding='utf-8') as f:
            sql_content = f.read()

        if filename == '02_dml_seed_data.sql':
            sql_content = sql_content.replace(
                '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e',
                pw_hash
            )

        cur.execute(sql_content)
        conn.commit()

    conn.close()
    print("Database schema, seed data, views, triggers, stored procedures, and security rules loaded successfully.")
    print("Default users created with password: password123")
    print("Done. Run 'python run.py' or 'flask run' to start the server.")

if __name__ == '__main__':
    app.run(debug=True)
