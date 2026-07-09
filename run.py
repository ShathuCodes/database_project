from app import create_app
from app import database

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Create tables and seed sample data with a real bcrypt hash for all demo users."""
    # pyrefly: ignore [missing-import]
    import bcrypt
    from app import database
    print("Creating schema...")
    with open('db_schema/schema.sql') as f:
        schema = f.read()
    conn = database.get_connection()
    cur  = conn.cursor()
    cur.execute(schema)
    conn.commit()

    print("Seeding database...")
    with open('db_schema/seed.sql') as f:
        seed_sql = f.read()

    # seed.sql ships with one placeholder bcrypt hash reused for every demo
    # user (login password "password123"); swap it for a freshly-generated
    # hash so the app can actually verify it.
    pw_hash = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode()
    seed_sql = seed_sql.replace(
        '$2b$12$KIXQwYyN2s0Z0m7C7d1uWuU4o9v4b1K3f8N1qz1s0lQe5T1c1YB0e',
        pw_hash
    )

    cur.execute(seed_sql)
    conn.commit()
    conn.close()
    print("Database schema and seed data created successfully.")
    print("Default users created with password: password123")
    print("Done. Run 'python run.py' or 'flask run' to start the server.")

if __name__ == '__main__':
    app.run(debug=True)
