from app import create_app
from app import database
import sys

app = create_app()


@app.cli.command('init-db')
def init_db():
    """Initialise the database.

    Safe by default — skips DDL and seeding if the schema already exists
    so that existing registered accounts and data are preserved.

    Pass --force to do a full wipe-and-rebuild:
        python run.py init-db --force
    """
    import bcrypt
    from app import database

    force = '--force' in sys.argv

    conn = database.get_connection()
    cur  = conn.cursor()

    # ── Check whether the schema is already set up ────────────────
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'app_user'
    """)
    already_exists = cur.fetchone()[0] > 0

    if already_exists and not force:
        print("=" * 60)
        print("  Database schema already exists — skipping DDL & seed.")
        print("  Your accounts and data have been preserved.")
        print()
        print("  To do a FULL RESET (wipes everything):")
        print("      python run.py init-db --force")
        print("=" * 60)

        # Still (re)apply views / triggers / stored procs / security
        # because those are safe to run again (CREATE OR REPLACE)
        safe_files = [
            ('03_views.sql',               'Refreshing analytical views...'),
            ('04_triggers_and_functions.sql','Refreshing triggers & functions...'),
            ('05_stored_procedures.sql',   'Refreshing stored procedures...'),
            ('06_security_and_rbac.sql',   'Refreshing security & RBAC rules...'),
        ]
        for filename, msg in safe_files:
            print(msg)
            with open(f'db_schema/{filename}', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            try:
                cur.execute(sql_content)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"  Warning: {filename} — {e}")

        conn.close()
        print("Done. Run 'python run.py' to start the server.")
        return

    # ── Full initialisation (first run, or --force) ───────────────
    if force:
        print("=" * 60)
        print("  --force flag detected: wiping and rebuilding everything.")
        print("=" * 60)

    pw_hash = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode()

    sql_files = [
        ('01_ddl_schema.sql',            'Creating DDL schema & indexes...'),
        ('02_dml_seed_data.sql',         'Seeding initial database records...'),
        ('03_views.sql',                 'Creating analytical views...'),
        ('04_triggers_and_functions.sql','Creating audit & status triggers...'),
        ('05_stored_procedures.sql',     'Creating stored procedures...'),
        ('06_security_and_rbac.sql',     'Applying database-level security & RBAC...'),
    ]

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
    print()
    print("Database initialised successfully.")
    print("Default demo users created with password: password123")
    print("Done. Run 'python run.py' to start the server.")


if __name__ == '__main__':
    app.run(debug=True)
