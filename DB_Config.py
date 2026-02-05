import os
import time
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

def get_db_connection(retries: int = 10, wait_seconds: int = 3):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return mysql.connector.connect(**db_config)
        except mysql.connector.Error as e:
            last_err = e
            print(f"Wachten op MySQL... poging {attempt}/{retries}")
            time.sleep(wait_seconds)

    raise Exception(f"Kon geen verbinding maken met MySQL na {retries} pogingen. Laatste fout: {last_err}")


if __name__ == "__main__":
    print("DB_NAME =", os.getenv("DB_NAME"))
    print("DB_HOST =", os.getenv("DB_HOST"))
    print("DB_PORT =", os.getenv("DB_PORT"))
