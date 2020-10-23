import psycopg2
from datetime import datetime


conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="password",
    host="127.0.0.1",
    port="5432",
)
cursor = conn.cursor()


def create_batch(batch_id: str):
    sql = """ INSERT INTO cpqCodeCompartor.status (batch_id, status, started, ended, error) VALUES (%s,%s,%s,%s,%s)"""
    cursor.execute(sql, (batch_id, "In-Progress", datetime.now(), None, None))
    conn.commit()
    print("Database updated successfully........")


def update_batch(batch_id: str, status: str, error: str = None):
    time = datetime.now()
    sql = """Update cpqCodeCompartor.status set status = %s, ended = %s, error = %s where batch_id = %s"""
    cursor.execute(sql, (status, time, error, batch_id))
    print("Database updated successfully........")
    conn.commit()
