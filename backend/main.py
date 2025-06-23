from fastapi import FastAPI
from backend.db import get_db_connection

app = FastAPI()

@app.get("/tvl/{protocol_name}")
def get_latest_tvl(protocol_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tvl, snapshot_time FROM tvl_snapshots
        WHERE protocol_name ilike %s
        ORDER BY snapshot_time DESC LIMIT 1
    """, (protocol_name,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return {"protocol": protocol_name, "tvl": row[0], "timestamp": row[1]}
    else:
        return {"error": "No TVL data found"}
