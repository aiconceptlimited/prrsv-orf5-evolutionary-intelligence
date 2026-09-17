import mysql.connector
import os

config = {
    'host': 'localhost',
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': 'prrsv_genomics'
}

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), '../database/schema.sql')

def reset_db():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE();")
    for (table_name,) in cursor.fetchall():
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    with open(SCHEMA_FILE, 'r') as f:
        for stmt in f.read().split(';'):
            if stmt.strip():
                cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database reset complete.")

if __name__ == "__main__":
    reset_db()

