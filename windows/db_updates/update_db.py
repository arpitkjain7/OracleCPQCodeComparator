import sqlite3
from datetime import datetime


def create_batch(batch_id: str):
    conn = sqlite3.connect("cpq_code_compare.db")
    sql = """ INSERT INTO BATCH_STATUS (BATCH_ID,STATUS,START_TIME,END_TIME,ERROR) VALUES (?,?,?,?,?)"""
    conn.execute(sql, (batch_id, "In-Progress", datetime.now(), None, None))
    conn.commit()
    print("Database updated successfully........")
    conn.close()


def update_batch(batch_id: str, status: str, error: str = None):
    conn = sqlite3.connect("cpq_code_compare.db")
    time = datetime.now()
    sql = """Update BATCH_STATUS SET STATUS=?,END_TIME=?,ERROR=? WHERE BATCH_ID = ?"""
    conn.execute(sql, (status, time, error, batch_id))
    print("Database updated successfully........")
    conn.commit()
    conn.close()
