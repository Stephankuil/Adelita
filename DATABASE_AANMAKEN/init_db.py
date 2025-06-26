import sqlite3
import json
with open("paddenstoelen_dataset.json", "r", encoding="utf-8") as f:
    paddenstoelen = json.load(f)

from DATABASE_AANMAKEN.planten_met_info import (
    planten_info,
)  # Importeer plantgegevens uit extern bestand
from Supplementen_lijst import supplementen  # Importeer supplementgegevens

# Verbind met de SQLite-database (maakt bestand aan als het nog niet bestaat)
conn = sqlite3.connect("../fytotherapie.db")
cursor = conn.cursor()

# Voer SQL-script uit voor het aanmaken van alle benodigde tabellen als ze nog niet bestaan
cursor.executescript(
    """
-- Tabel voor planteninformatie
CREATE TABLE IF NOT EXISTS planten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL UNIQUE,
    botanische_naam TEXT,
    beschrijving TEXT,
    te_gebruiken_bij TEXT,
    gebruikt_plantendeel TEXT,
    aanbevolen_combinaties TEXT,
    niet_te_gebruiken_bij TEXT,
    categorie_kleur TEXT,
    details TEXT,
    afbeelding TEXT
);

-- Tabel voor klachten
CREATE TABLE IF NOT EXISTS klachten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL UNIQUE,
    beschrijving TEXT
);

-- Koppeltabel voor relatie tussen planten en klachten
CREATE TABLE IF NOT EXISTS plant_klacht (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    klacht_id INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES planten(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

-- Tabel voor klantgegevens
CREATE TABLE IF NOT EXISTS klanten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    emailadres TEXT,
    telefoon TEXT,
    adres TEXT
);

-- Notities per klant
CREATE TABLE IF NOT EXISTS notities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    inhoud TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

-- Afspraken met klanten
CREATE TABLE IF NOT EXISTS afspraken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    datumtijd TEXT,
    onderwerp TEXT,
    locatie TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

-- Behandelingen die zijn uitgevoerd
CREATE TABLE IF NOT EXISTS behandelingen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    naam TEXT,
    datum TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

-- Klachten gekoppeld aan behandelingen
CREATE TABLE IF NOT EXISTS behandeling_klacht (
    behandeling_id INTEGER,
    klacht_id INTEGER,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

-- Planten gekoppeld aan behandelingen
CREATE TABLE IF NOT EXISTS behandeling_plant (
    behandeling_id INTEGER,
    plant_id INTEGER,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (plant_id) REFERENCES planten(id)
);

-- Supplementenlijst met info
CREATE TABLE supplementen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    andere_namen TEXT,
    lost_op_in TEXT,
    eigenschap_functie TEXT,
    bij_tekort TEXT,
    inzetten_bij TEXT,
    voedingsbronnen TEXT,
    bijzonderheden TEXT,
    bouwstof TEXT,
    eigenschappen TEXT
);
CREATE TABLE IF NOT EXISTS paddenstoelen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nederlandse_naam TEXT NOT NULL,
    andere_namen TEXT,
    familie TEXT,
    belangrijkste_werkzame_stoffen TEXT,
    toepassing TEXT,
    werking TEXT
);
"""
)
for item in paddenstoelen:
    # Converteer naam altijd naar string
    naam_raw = item.get("nederlandse_naam", "")
    if isinstance(naam_raw, list):
        nederlandse_naam = ", ".join(naam_raw)
    else:
        nederlandse_naam = str(naam_raw)

    andere_namen = json.dumps({
        "latijns": item.get("latijnse_naam"),
        "japanse_naam": item.get("japanse_naam"),
        "chinese_naam_tcm": item.get("chinese_naam_tcm"),
        "algemene_naam": item.get("algemene_naam"),
        "internationale_naam": item.get("internationale_naam"),
        "maleisische_naam": item.get("maleisische_naam")
    }, ensure_ascii=False)

    familie = item.get("familie", "")
    stoffen = json.dumps(item.get("belangrijkste_werkzame_stoffen", []), ensure_ascii=False)
    toepassing = json.dumps(item.get("toepassing", []), ensure_ascii=False)
    werking = json.dumps(item.get("werking", []), ensure_ascii=False)

    cursor.execute("""
        INSERT INTO paddenstoelen (
            nederlandse_naam, andere_namen, familie,
            belangrijkste_werkzame_stoffen, toepassing, werking
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nederlandse_naam, andere_namen, familie, stoffen, toepassing, werking))


# Voeg planten toe aan de database, maar alleen als ze nog niet bestaan
for plant in planten_info:
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant["naam"],))
    result = cursor.fetchone()
    if not result:
        cursor.execute(
            """
            INSERT INTO planten (
                naam, botanische_naam, beschrijving, te_gebruiken_bij,
                gebruikt_plantendeel, aanbevolen_combinaties, niet_te_gebruiken_bij,
                categorie_kleur, details, afbeelding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                plant["naam"],
                plant["botanische_naam"],
                plant["beschrijving"],
                plant["te_gebruiken_bij"],
                plant["gebruikt_plantendeel"],
                plant["aanbevolen_combinaties"],
                plant["niet_te_gebruiken_bij"],
                plant.get("categorie_kleur", ""),  # optioneel veld
                plant["details"],
                plant["afbeelding"],
            ),
        )
    else:
        print(f"⏩ Plant '{plant['naam']}' bestaat al, overslaan.")

# Voeg supplementen toe aan de database, als ze nog niet bestaan
for supplement in supplementen:
    cursor.execute("SELECT id FROM supplementen WHERE naam = ?", (supplement["naam"],))
    result = cursor.fetchone()

    if not result:
        cursor.execute(
            """
            INSERT INTO supplementen (
                naam, andere_namen, lost_op_in, eigenschap_functie,
                bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden,
                bouwstof, eigenschappen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
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
            ),
        )
        print(f"✅ Toegevoegd: {supplement['naam']}")
    else:
        print(f"⏩ Bestaat al: {supplement['naam']}")

# Geef het aantal supplementen dat is verwerkt
print(f"{len(supplementen)} supplement(en) toegevoegd aan de database!")

# Sla alle wijzigingen op en sluit de databaseverbinding
conn.commit()
conn.close()

print("✅ Planten succesvol toegevoegd aan de database.")
