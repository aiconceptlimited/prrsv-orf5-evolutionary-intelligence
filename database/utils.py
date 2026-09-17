import os
import mysql.connector

config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'prrsv_genomics')
}

def get_connection():
    return mysql.connector.connect(**config)

def execute_query(query, data=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, data or ())
    result = cursor.fetchall() if fetch else None
    conn.commit()
    cursor.close()
    conn.close()
    return result

