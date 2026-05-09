import sqlite3

def check_db(db_path):
    print(f"--- Checking {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {len(tables)}")
        
        # Check specific counts if they exist
        for table in ['core_club', 'core_event', 'core_preregisteredattendee', 'core_user']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Table {table}: {count} rows")
            except:
                pass
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub\\db.sqlite3')
    check_db('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub\\campushubdb.sqlite3')
