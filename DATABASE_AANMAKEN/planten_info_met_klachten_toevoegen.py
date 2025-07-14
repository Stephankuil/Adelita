import mysql.connector
from planten_met_info import planten_info
from nieuwe_lijst_klachten_en_beschrijvingen import klacht_beschrijvingen_1
from dotenv import load_dotenv
import os

load_dotenv()

# Verbind met MySQL
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4"
)
cursor = conn.cursor()

for plant in planten_info:
    plant_naam = plant["naam"]

    # Zoek plant-ID
    cursor.execute("SELECT id FROM planten WHERE naam = %s", (plant_naam,))
    result = cursor.fetchone()
    if not result:
        print(f"🌿 Plant niet gevonden: {plant_naam}")
        continue
    plant_id = result[0]

    # Verwerk klachten
    ruwe_klachten = plant.get("te_gebruiken_bij", [])
    if isinstance(ruwe_klachten, str):
        klachten = [k.strip().capitalize() for k in ruwe_klachten.split(",") if k.strip()]
    elif isinstance(ruwe_klachten, list):
        klachten = [k.strip().capitalize() for k in ruwe_klachten if k.strip()]
    else:
        klachten = []

    for klacht_naam in klachten:
        beschrijving = klacht_beschrijvingen_1.get(klacht_naam, "")

        # Voeg klacht toe als die nog niet bestaat
        cursor.execute("SELECT id FROM klachten WHERE naam = %s", (klacht_naam,))
        klacht_result = cursor.fetchone()

        if not klacht_result:
            cursor.execute(
                "INSERT INTO klachten (naam, beschrijving) VALUES (%s, %s)",
                (klacht_naam, beschrijving),
            )
            klacht_id = cursor.lastrowid
            print(f"🩺 Klacht toegevoegd: {klacht_naam}")
        else:
            klacht_id = klacht_result[0]

        # Voeg koppeling toe als die nog niet bestaat
        cursor.execute(
            "SELECT 1 FROM plant_klacht WHERE plant_id = %s AND klacht_id = %s",
            (plant_id, klacht_id),
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (%s, %s)",
                (plant_id, klacht_id),
            )

conn.commit()
cursor.close()
conn.close()

print("✅ Alle klachten en koppelingen zijn toegevoegd aan MySQL.")
