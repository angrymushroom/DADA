from fastapi import FastAPI, HTTPException
from backend.db import get_db_connection
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#@app.get("/tvl/{protocol_name}")
#def get_latest_tvl(protocol_name: str):
#    conn = get_db_connection()
#    cursor = conn.cursor()
#    cursor.execute("""
#        SELECT tvl, snapshot_time FROM tvl_snapshots
#        WHERE protocol_name ilike %s
#        ORDER BY snapshot_time DESC LIMIT 1
#    """, (protocol_name,))
#    row = cursor.fetchone()
#    cursor.close()
#    conn.close()
#
#    if row:
#        return {"protocol": protocol_name, "tvl": row[0], "timestamp": row[1]}
#    else:
#        return {"error": "No TVL data found"}
@app.get("/tvl/{protocol_name}")
def get_tvl_time_series(protocol_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT snapshot_time, tvl
        FROM tvl_snapshots
        WHERE protocol_name ILIKE %s
        ORDER BY snapshot_time ASC
    """, (protocol_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No TVL data found.")

    return [
        {
            "timestamp": row[0].isoformat(),
            "tvl": row[1]
        }
        for row in rows
    ]

@app.get("/risk/{protocol_name}")
def get_risk_metrics(protocol_name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT metric_name, metric_value, collected_at
        FROM risk_metrics
        WHERE protocol_name = %s
        ORDER BY collected_at DESC
        LIMIT 10
    """, (protocol_name.lower(),))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No risk metrics found.")
    metrics = [
        {
            "metric": row[0],
            "value": float(row[1]),
            "timestamp": row[2].isoformat()
        }
        for row in rows
    ]
    return {
        "protocol": protocol_name,
        "metrics": metrics
    }
