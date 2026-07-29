import os
import sqlite3

_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patentes.db")
conn = sqlite3.connect(_DB)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS autorizadas")
cur.execute("""
    CREATE TABLE IF NOT EXISTS autorizadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patente TEXT UNIQUE NOT NULL
    )
""")

patentes = ["AA123BB", "ABC123", "NVZ087", "AA426XS"]
for p in patentes:
    cur.execute("INSERT OR IGNORE INTO autorizadas (patente) VALUES (?)", (p,))

conn.commit()
conn.close()
print("BD creada con", len(patentes), "patentes de prueba.")
