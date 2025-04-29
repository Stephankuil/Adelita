import sqlite3
from planten_met_info import planten_info
from nieuwe_lijst_klachten_en_beschrijvingen import klacht_beschrijvingen_1  # <- nieuwe import

# Verbind met de database
conn = sqlite3.connect("fytotherapie.db")
cursor = conn.cursor()

for plant in planten_info:
    plant_naam = plant["naam"]

    # Zoek plant_id
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    result = cursor.fetchone()
    if not result:
        print(f"Plant niet gevonden in database: {plant_naam}")
        continue
    plant_id = result[0]

    # Zorg dat klachten een lijst is, ook als het oorspronkelijk een string is
    ruwe_klachten = plant.get("te_gebruiken_bij", [])
    if isinstance(ruwe_klachten, str):
        klachten = [k.strip().capitalize() for k in ruwe_klachten.split(",") if k.strip()]
    elif isinstance(ruwe_klachten, list):
        klachten = [k.strip().capitalize() for k in ruwe_klachten if k.strip()]
    else:
        klachten = []

    for klacht_naam in klachten:
        # Haal beschrijving op uit klacht_beschrijvingen_1
        beschrijving = klacht_beschrijvingen_1.get(klacht_naam, "")

        # Voeg klacht toe als deze nog niet bestaat
        cursor.execute("SELECT id FROM klachten WHERE naam = ?", (klacht_naam,))
        klacht_result = cursor.fetchone()
        if not klacht_result:
            cursor.execute(
                "INSERT INTO klachten (naam, beschrijving) VALUES (?, ?)",
                (klacht_naam, beschrijving)
            )
            klacht_id = cursor.lastrowid
            print(f"Nieuwe klacht toegevoegd: {klacht_naam} (met beschrijving)")
        else:
            klacht_id = klacht_result[0]

        # Voeg koppeling toe als die nog niet bestaat
        cursor.execute(
            "SELECT 1 FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?",
            (plant_id, klacht_id),
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)",
                (plant_id, klacht_id),
            )

# Opslaan en sluiten
conn.commit()
conn.close()

print("✅ Alle plant-klacht koppelingen zijn succesvol verwerkt.")
