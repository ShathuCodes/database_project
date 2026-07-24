import app.database as db

def print_table(table_name, limit=5):
    rows = db.fetchall(f"SELECT * FROM {table_name} LIMIT {limit}")
    print(f"\n{"="*60}")
    print(f" TABLE: {table_name.upper()} (Showing up to {limit} rows)")
    print(f"{"="*60}")
    if not rows:
        print(" [No records found]")
        return
    
    headers = list(rows[0].keys())
    # Format header
    header_str = " | ".join(f"{h:<18}" for h in headers)
    print(header_str)
    print("-" * len(header_str))
    
    for row in rows:
        row_str = " | ".join(f"{str(row[h]):<18}" for h in headers)
        print(row_str)

if __name__ == '__main__':
    tables = [r['table_name'] for r in db.fetchall("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")]
    print(f"Found {len(tables)} tables in database:")
    for t in tables:
        print(f" - {t}")
        
    # Print sample tables
    sample_tables = ['app_user', 'patient', 'case_master', 'postmortem_examination', 'lab_request', 'audit_log']
    for st in sample_tables:
        if st in tables:
            print_table(st, limit=5)
