import os
from dotenv import load_dotenv
import mysql.connector
import time

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST", "mysql"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "ssl_ca": os.getenv("DB_SSL_CA"),         # CA-certificaat
    "ssl_cert": os.getenv("DB_SSL_CERT"),     # Client-certificaat
    "ssl_key": os.getenv("DB_SSL_KEY"),       # Client-private key
}
def get_db_connection():
    for attempt in range(10):
        try:
            return mysql.connector.connect(**db_config)
        except mysql.connector.Error as e:
            print(f"⏳ Wachten op MySQL... poging {attempt+1}/10")
            time.sleep(5)
    raise Exception("❌ Kon geen verbinding maken met MySQL na 10 pogingen.")