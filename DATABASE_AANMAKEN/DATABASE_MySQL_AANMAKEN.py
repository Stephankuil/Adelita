import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import json

from DATABASE_AANMAKEN.planten_met_info import planten_info
from Supplementen_lijst import supplementen

load_dotenv()

# 🔐 Haal credentials uit .env
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}
db_name = os.getenv("DB_NAME")

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# ✅ Maak tabellen aan
tables = {}

tables["planten"] = """
CREATE TABLE IF NOT EXISTS planten (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naam VARCHAR(255) NOT NULL UNIQUE,
    botanische_naam TEXT,
    beschrijving TEXT,
    te_gebruiken_bij TEXT,
    gebruikt_plantendeel TEXT,
    aanbevolen_combinaties TEXT,
    niet_te_gebruiken_bij TEXT,
    categorie_kleur TEXT,
    details TEXT,
    afbeelding TEXT
)
"""
tables["gebruikers"] = """
CREATE TABLE IF NOT EXISTS gebruikers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gebruikersnaam VARCHAR(255) NOT NULL UNIQUE,
    wachtwoord_hash TEXT NOT NULL,
    rol VARCHAR(50) DEFAULT 'gebruiker'
)
"""


tables["klachten"] = """
CREATE TABLE IF NOT EXISTS klachten (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naam VARCHAR(255) NOT NULL UNIQUE,
    beschrijving TEXT
)
"""

tables["plant_klacht"] = """
CREATE TABLE IF NOT EXISTS plant_klacht (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    klacht_id INT NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES planten(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
)
"""

tables["klanten"] = """
CREATE TABLE IF NOT EXISTS klanten (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naam VARCHAR(255) NOT NULL,
    emailadres TEXT,
    telefoon TEXT,
    adres TEXT
)
"""

tables["notities"] = """
CREATE TABLE IF NOT EXISTS notities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    klant_id INT,
    inhoud TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
)
"""

tables["afspraken"] = """
CREATE TABLE IF NOT EXISTS afspraken (
    id INT AUTO_INCREMENT PRIMARY KEY,
    klant_id INT,
    datumtijd DATETIME,
    onderwerp TEXT,
    locatie TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
)
"""

tables["behandelingen"] = """
CREATE TABLE IF NOT EXISTS behandelingen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    klant_id INT,
    naam TEXT,
    datum DATE,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
)
"""

tables["behandeling_klacht"] = """
CREATE TABLE IF NOT EXISTS behandeling_klacht (
    behandeling_id INT,
    klacht_id INT,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
)
"""

tables["behandeling_plant"] = """
CREATE TABLE IF NOT EXISTS behandeling_plant (
    behandeling_id INT,
    plant_id INT,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (plant_id) REFERENCES planten(id)
)
"""

tables["supplementen"] = """
CREATE TABLE IF NOT EXISTS supplementen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naam VARCHAR(255) NOT NULL,
    andere_namen TEXT,
    lost_op_in TEXT,
    eigenschap_functie TEXT,
    bij_tekort TEXT,
    inzetten_bij TEXT,
    voedingsbronnen TEXT,
    bijzonderheden TEXT,
    bouwstof TEXT,
    eigenschappen TEXT
)
"""

tables["paddenstoelen"] = """
CREATE TABLE IF NOT EXISTS paddenstoelen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nederlandse_naam TEXT NOT NULL,
    japanse_naam TEXT,
    chinese_naam TEXT,
    latijnse_naam TEXT,
    familie TEXT,
    belangrijkste_werkzame_stoffen TEXT,
    toepassing TEXT,
    werking TEXT
)
"""

for name, ddl in tables.items():
    cursor.execute(ddl)

def to_string(value):
    if isinstance(value, list):
        return ", ".join(value)
    elif value is None:
        return ""
    else:
        return str(value)


# ✅ Voeg paddenstoelen toe
with open("paddenstoelen_dataset.json", "r", encoding="utf-8") as f:
    paddenstoelen = json.load(f)

for item in paddenstoelen:
    naam_raw = item.get("nederlandse_naam", "")
    nederlandse_naam = ", ".join(naam_raw) if isinstance(naam_raw, list) else str(naam_raw)

    japanse_naam = to_string(item.get("japanse_naam", ""))
    chinese_naam = to_string(item.get("chinese_naam_tcm", ""))
    latijnse_naam = to_string(item.get("latijnse_naam", ""))

    familie = item.get("familie", "")
    stoffen = json.dumps(item.get("belangrijkste_werkzame_stoffen", []), ensure_ascii=False)
    toepassing = json.dumps(item.get("toepassing", []), ensure_ascii=False)
    werking = json.dumps(item.get("werking", []), ensure_ascii=False)

    cursor.execute("""
        INSERT INTO paddenstoelen (
            nederlandse_naam, japanse_naam, chinese_naam, latijnse_naam, familie,
            belangrijkste_werkzame_stoffen, toepassing, werking
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nederlandse_naam, japanse_naam, chinese_naam, latijnse_naam, familie, stoffen, toepassing, werking))



# ✅ Voeg planten toe
for plant in planten_info:
    cursor.execute("SELECT id FROM planten WHERE naam = %s", (plant["naam"],))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO planten (
                naam, botanische_naam, beschrijving, te_gebruiken_bij,
                gebruikt_plantendeel, aanbevolen_combinaties, niet_te_gebruiken_bij,
                categorie_kleur, details, afbeelding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            plant["naam"],
            plant["botanische_naam"],
            plant["beschrijving"],
            plant["te_gebruiken_bij"],
            plant["gebruikt_plantendeel"],
            plant["aanbevolen_combinaties"],
            plant["niet_te_gebruiken_bij"],
            plant.get("categorie_kleur", ""),
            plant["details"],
            plant["afbeelding"],
        ))

# ✅ Voeg supplementen toe
for supplement in supplementen:
    cursor.execute("SELECT id FROM supplementen WHERE naam = %s", (supplement["naam"],))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO supplementen (
                naam, andere_namen, lost_op_in, eigenschap_functie,
                bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden,
                bouwstof, eigenschappen
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            supplement.get("naam", ""),
            supplement.get("andere_namen", ""),
            supplement.get("lost_op_in", ""),
            supplement.get("eigenschap_functie", supplement.get("eigenschap", "")),
            supplement.get("bij_tekort", ""),
            supplement.get("inzetten_bij", ""),
            supplement.get("voedingsbronnen", ""),
            supplement.get("bijzonderheden", ""),
            supplement.get("bouwstof", ""),
            supplement.get("eigenschappen", supplement.get("overige", "")),
        ))

# ✅ Afronden
conn.commit()
cursor.close()
conn.close()

print("✅ Alle tabellen aangemaakt en data succesvol toegevoegd aan MySQL.")
