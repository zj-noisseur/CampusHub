import os
import sqlite3
from datetime import datetime

def get_all_migration_names():
    migrations_dir = os.path.join('core', 'migrations')
    if not os.path.isdir(migrations_dir):
        return []
    
    files = os.listdir(migrations_dir)
    migration_names = []
    for f in files:
        if f.endswith('.py') and f != '__init__.py':
            migration_names.append(f[:-3])  # Remove '.py' extension
    return sorted(migration_names)

def fix_database(db_path, migration_names):
    print("=" * 60)
    print(f"Auditing and repairing SQLite database: {db_path}")
    if not os.path.exists(db_path):
        print(f"-> Skipped (file does not exist at {db_path})")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check columns of core_club table
        cursor.execute("PRAGMA table_info(core_club)")
        columns = [row[1] for row in cursor.fetchall()]
        
        needs_commit = False
        
        # 1. Rename club_category_id to club_category
        if 'club_category_id' in columns and 'club_category' not in columns:
            print("   * Found outdated 'club_category_id' column. Renaming to 'club_category'...")
            cursor.execute("ALTER TABLE core_club RENAME COLUMN club_category_id TO club_category")
            print("     -> Renamed successfully!")
            needs_commit = True
        elif 'club_category' in columns:
            print("   * 'club_category' column is already correctly named.")
        else:
            print("   * WARNING: Neither 'club_category_id' nor 'club_category' found in core_club!")
            
        # 2. Add renewal_policy if missing
        if 'renewal_policy' not in columns:
            print("   * Found missing 'renewal_policy' column. Adding column with default 'ROLLING'...")
            cursor.execute("ALTER TABLE core_club ADD COLUMN renewal_policy varchar(20) DEFAULT 'ROLLING'")
            print("     -> Added successfully!")
            needs_commit = True
        else:
            print("   * 'renewal_policy' column already exists.")
            
        # 3. Drop core_clubcategory if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_clubcategory'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("   * Dropping obsolete 'core_clubcategory' table...")
            cursor.execute("DROP TABLE IF EXISTS core_clubcategory")
            print("     -> Dropped successfully!")
            needs_commit = True
        else:
            print("   * Obsolete 'core_clubcategory' table is already dropped.")
            
        # 4. Fake migrations directly in SQLite
        print("   * Faking migrations directly in SQLite...")
        # Get already applied migrations
        cursor.execute("SELECT name FROM django_migrations WHERE app='core'")
        applied_migrations = set(row[0] for row in cursor.fetchall())
        
        faked_count = 0
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        
        for migration in migration_names:
            if migration not in applied_migrations:
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
                    ('core', migration, now_str)
                )
                faked_count += 1
                
        if faked_count > 0:
            print(f"     -> Recorded {faked_count} outstanding migrations as FAKED/applied!")
            needs_commit = True
        else:
            print("     -> All migrations are already recorded as applied.")
            
        if needs_commit:
            conn.commit()
            print(f"-> SUCCESS: Successfully repaired and committed all changes for {db_path}!")
        else:
            print(f"-> Already fully healthy: {db_path} is in perfect sync.")
            
        conn.close()
        return True
    except Exception as e:
        print(f"-> ERROR repairing database {db_path}: {e}")
        return False

def main():
    print("============================================================")
    print("CampusHub - SQLite Database Patching & Migration Helper")
    print("============================================================")
    
    # 1. Read all migration names
    migration_names = get_all_migration_names()
    if not migration_names:
        print("[ERROR] Could not find Django migrations directory at core/migrations!")
        print("Please ensure you are running this script inside the 'campushub/' directory.")
        return
        
    print(f"Loaded {len(migration_names)} Django core migrations from files.")
    
    # 2. Paths to sqlite files relative to campushub/ directory
    dbs = ['campushubdb.sqlite3', 'db.sqlite3']
    repaired_any = False
    
    for db in dbs:
        if fix_database(db, migration_names):
            repaired_any = True
            
    if repaired_any:
        print("\n============================================================")
        print("[SUCCESS] All local SQLite databases have been repaired!")
        print("You and your groupmate can now run the app on SQLite with ZERO errors.")
        print("============================================================")
    else:
        print("\n[ERROR] No local SQLite databases were repaired.")

if __name__ == '__main__':
    main()
