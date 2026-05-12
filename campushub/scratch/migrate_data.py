import sqlite3
import os
import uuid

# Paths to databases
OLD_DB = 'campushub/db_old.sqlite3'
NEW_DB = 'campushub/db.sqlite3'

def run_migration():
    if not os.path.exists(OLD_DB):
        print(f"Error: {OLD_DB} not found. Please ensure the old database is renamed to db_old.sqlite3")
        return

    conn_old = sqlite3.connect(OLD_DB)
    conn_new = sqlite3.connect(NEW_DB)
    c_old = conn_old.cursor()
    c_new = conn_new.cursor()

    category_map = {}

    def copy_table(table_name, target_cols=None, transform_func=None):
        print(f"Migrating {table_name}...")
        try:
            # Get old columns
            c_old.execute(f"PRAGMA table_info(\"{table_name}\")")
            old_cols = [col[1] for col in c_old.fetchall()]
            
            # Get data
            c_old.execute(f"SELECT * FROM \"{table_name}\"")
            rows = c_old.fetchall()
            
            if not rows:
                print(f" - No data found in {table_name}")
                return

            # If target_cols not specified, assume same as old
            if not target_cols:
                target_cols = old_cols.copy()
                
            placeholders = ", ".join(["?"] * len(target_cols))
            cols_str = ", ".join([f"\"{c}\"" for c in target_cols])
            insert_query = f"INSERT INTO \"{table_name}\" ({cols_str}) VALUES ({placeholders})"
            
            count = 0
            for row in rows:
                data = list(row)
                if transform_func:
                    data = transform_func(data, old_cols, c_new, category_map)
                
                if data is None: continue

                try:
                    c_new.execute(insert_query, data)
                    count += 1
                except Exception as e:
                    print(f"   ! Error inserting row {data[0]} in {table_name}: {e}")
            
            conn_new.commit()
            print(f" - Successfully migrated {count} rows")
        except Exception as e:
            print(f" - Error migrating {table_name}: {e}")

    # --- Transforms ---

    def transform_club(data, old_cols, c_new, cat_map):
        d = dict(zip(old_cols, data))
        cat_name = d.get('category')
        cat_id = None
        if cat_name:
            if cat_name not in cat_map:
                c_new.execute("INSERT OR IGNORE INTO core_clubcategory (name) VALUES (?)", (cat_name,))
                c_new.execute("SELECT id FROM core_clubcategory WHERE name = ?", (cat_name,))
                cat_map[cat_name] = c_new.fetchone()[0]
            cat_id = cat_map[cat_name]

        return [
            d.get('id'), d.get('name'), d.get('description', ''), d.get('is_claimed', 0),
            d.get('membership_fee', 0.0), d.get('payment_qr_code'), d.get('ig_handle'),
            d.get('valid_till'), d.get('logo'), d.get('banner'), d.get('payment_qr'),
            d.get('social_instagram'), d.get('social_linkedin'), d.get('social_facebook'),
            d.get('social_twitter'), d.get('social_website'), d.get('social_discord'),
            d.get('last_fetched_date'), d.get('posts_count', 0), d.get('renewal_policy', 'ROLLING'),
            cat_id, d.get('institution_id')
        ]

    def transform_post(data, old_cols, *args):
        d = dict(zip(old_cols, data))
        return [d.get('id'), d.get('short_code'), d.get('caption'), d.get('category', 'MISC'), d.get('timestamp'), d.get('club_id')]

    def transform_user(data, old_cols, *args):
        d = dict(zip(old_cols, data))
        try:
            formatted_id = str(uuid.UUID(d['id']))
        except:
            formatted_id = str(uuid.uuid4())
        
        student_name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip() or d.get('username', 'User')
        
        return [
            formatted_id, d.get('password'), d.get('last_login'), d.get('is_superuser', 0),
            d.get('email'), student_name, d.get('student_id'), d.get('phone_number'),
            d.get('bio'), d.get('profile_picture'), d.get('alternative_email'),
            d.get('faculty'), d.get('major'), d.get('year_of_study'),
            d.get('is_active', 1), d.get('is_staff', 0)
        ]

    # --- Run Migration ---
    copy_table("core_state")
    copy_table("core_institution")
    
    club_cols = ['id', 'name', 'description', 'is_claimed', 'membership_fee', 'payment_qr_code', 'ig_handle', 'valid_till', 'logo', 'banner', 'payment_qr', 'social_instagram', 'social_linkedin', 'social_facebook', 'social_twitter', 'social_website', 'social_discord', 'last_fetched_date', 'posts_count', 'renewal_policy', 'club_category_id', 'institution_id']
    copy_table("core_club", target_cols=club_cols, transform_func=transform_club)
    
    post_cols = ['id', 'short_code', 'caption', 'category', 'timestamp', 'club_id']
    copy_table("core_post", target_cols=post_cols, transform_func=transform_post)
    
    copy_table("core_postimage")
    
    user_cols = ['id', 'password', 'last_login', 'is_superuser', 'email', 'student_name', 'student_id', 'phone_number', 'bio', 'profile_picture', 'alternative_email', 'faculty', 'major', 'year_of_study', 'is_active', 'is_staff']
    copy_table("core_user", target_cols=user_cols, transform_func=transform_user)

    conn_old.close()
    conn_new.close()
    print("\nMigration Complete!")

if __name__ == "__main__":
    run_migration()
