from backend.db import get_db_connection

conn = get_db_connection()
print("✅ Connected successfully")
conn.close()
