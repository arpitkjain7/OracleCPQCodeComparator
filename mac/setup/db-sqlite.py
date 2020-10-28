import sqlite3

conn = sqlite3.connect("../cpq_code_compare.db")

print("Opened database successfully")

conn.execute(
    """CREATE TABLE BATCH_STATUS
         (BATCH_ID TEXT PRIMARY KEY     NOT NULL,
         STATUS           TEXT    NOT NULL,
         START_TIME            TEXT     NOT NULL,
         END_TIME        TEXT,
         ERROR          TEXT);"""
)
print("Table created successfully")

conn.close()
