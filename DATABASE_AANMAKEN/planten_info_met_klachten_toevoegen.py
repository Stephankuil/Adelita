import sqlite3
from planten_met_info import planten_info  # Lijst met planten en hun toepassingen
from nieuwe_lijst_klachten_en_beschrijvingen import klacht_beschrijvingen_1  # Dictionary: klacht -> beschrijving

# Verbind met de SQLite-database
conn = sqlite3.connect("../fytotherapie.db")
cursor = conn.cursor()

# Loop door alle planten in de lijst
for plant in planten_info:
    plant_naam = plant["naam"]

    # Zoek het ID van de plant in de database
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    result = cursor.fetchone()
    if not result:
        print(f"Plant niet gevonden in database: {plant_naam}")
        continue  # Sla deze plant over als hij niet bestaat
    plant_id = result[0]

    # Haal de gekoppelde klachten op (kan string of lijst zijn)
    ruwe_klachten = plant.get("te_gebruiken_bij", [])

    if isinstance(ruwe_klachten, str):
        # Als string: splits op komma's en maak lijst
        klachten = [k.strip().capitalize() for k in ruwe_klachten.split(",") if k.strip()]
    elif isinstance(ruwe_klachten, list):
        # Als lijst: schoon alle elementen op
        klachten = [k.strip().capitalize() for k in ruwe_klachten if k.strip()]
    else:
        klachten = []  # Geen geldige input

    for klacht_naam in klachten:
        # Haal optioneel een beschrijving uit de woordenlijst
        beschrijving = klacht_beschrijvingen_1.get(klacht_naam, "")

        # Voeg klacht toe aan database als deze nog niet bestaat
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

        # Controleer of koppeling plant-klacht al bestaat
        cursor.execute(
            "SELECT 1 FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?",
            (plant_id, klacht_id),
        )
        if not cursor.fetchone():
            # Voeg koppeling toe als die nog niet bestaat
            cursor.execute(
                "INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)",
                (plant_id, klacht_id),
            )

# Sla alle wijzigingen op en sluit verbinding met database
conn.commit()
conn.close()

print("✅ Alle plant-klacht koppelingen zijn succesvol verwerkt.")
