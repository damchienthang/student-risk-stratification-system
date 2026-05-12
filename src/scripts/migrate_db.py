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
        
    conn.commit()
    conn.close()
    print("Database migration completed successfully.")
except Exception as e:
    print(f"Error: {e}")
