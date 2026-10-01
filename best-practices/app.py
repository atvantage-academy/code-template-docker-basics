import os
from flask import Flask
import psycopg2

app = Flask(__name__)

# Konfiguration aus der Umgebung – die Werte dahinter gelten nur,
# solange nichts gesetzt ist.
DB_NAME = os.getenv("DB_NAME", "helloworld")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

@app.get("/")
def start():
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    cursor = connection.cursor()
    cursor.execute("SELECT text FROM gruss")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return "\n".join(row[0] for row in rows) + "\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
