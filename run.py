from app import create_app
from app import database

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Create tables and seed sample data with real bcrypt hashes."""
    # pyrefly: ignore [missing-import]
    import bcrypt
    from app import database
    print("Creating schema...")
    with open('db_schema/schema.sql') as f:
        schema = f.read()
    conn = database.get_connection()
    cur  = conn.cursor()
    cur.execute(schema)
    
    print("Seeding database...")
    with open('db_schema/seed.sql') as f:
        seed_sql = f.read()
    
    # Replace placeholder hashes with real bcrypt hashes
    pw_hash = bcrypt.hashpw(b'Password123', bcrypt.gensalt()).decode()
    seed_sql = seed_sql.replace("'$2b$12$placeholder_admin_hash_here'", f"'{pw_hash}'")
    seed_sql = seed_sql.replace("'$2b$12$placeholder_doctor_hash_here'", f"'{pw_hash}'")
    seed_sql = seed_sql.replace("'$2b$12$placeholder_jmo_hash_here'", f"'{pw_hash}'")
    seed_sql = seed_sql.replace("'$2b$12$placeholder_lab_hash_here'", f"'{pw_hash}'")
    seed_sql = seed_sql.replace("'$2b$12$placeholder_clerk_hash_here'", f"'{pw_hash}'")
    seed_sql = seed_sql.replace("'$2b$12$placeholder_police_hash_here'", f"'{pw_hash}'")
    
    cur.execute(seed_sql)
    conn.commit()
    conn.close()
    print("Database schema and seed data created successfully.")
    print("Default users created with password: Password123")
    print("Done. Run 'python run.py' or 'flask run' to start the server.")

if __name__ == '__main__':
    app.run(debug=True)
