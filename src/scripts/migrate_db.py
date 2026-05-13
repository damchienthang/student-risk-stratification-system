import sqlite3
import os

# Base directory (Root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(BASE_DIR, "data", "processed", "database.db")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    if "email" not in columns:
        print("Adding 'email' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    
    if "is_external" not in columns:
        print("Adding 'is_external' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_external BOOLEAN DEFAULT 0")

    if "phone_number" not in columns:
        print("Adding 'phone_number' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")

    if "is_active" not in columns:
        print("Adding 'is_active' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")

    # 2. Check inference_logs table
    cursor.execute("PRAGMA table_info(inference_logs)")
    inf_cols = [row[1] for row in cursor.fetchall()]
    
    if not inf_cols:
        print("Creating 'inference_logs' table...")
        cursor.execute("""
            CREATE TABLE inference_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id INTEGER,
                code_module TEXT,
                code_presentation TEXT,
                gender_num INTEGER,
                imd_band_num INTEGER,
                education_num INTEGER,
                age_num INTEGER,
                disability_num INTEGER,
                num_of_prev_attempts INTEGER,
                studied_credits INTEGER,
                total_clicks INTEGER,
                avg_score REAL,
                min_score REAL,
                n_submitted INTEGER,
                n_late INTEGER,
                avg_submit_delay REAL,
                reg_days_before INTEGER,
                risk_level INTEGER,
                risk_label TEXT,
                confidence REAL
            )
        """)
    else:
        # Add new columns if table exists but is old
        new_inf_cols = [
            ("user_id", "INTEGER"), ("min_score", "REAL"), ("n_submitted", "INTEGER"),
            ("n_late", "INTEGER"), ("avg_submit_delay", "REAL"), ("reg_days_before", "INTEGER")
        ]
        for col_name, col_type in new_inf_cols:
            if col_name not in inf_cols:
                print(f"Adding '{col_name}' column to inference_logs...")
                cursor.execute(f"ALTER TABLE inference_logs ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()
    print("Database migration completed successfully.")
except Exception as e:
    print(f"Error: {e}")
