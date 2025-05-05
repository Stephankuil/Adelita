import sqlite3
from DATABASE_AANMAKEN.planten_met_info import planten_info

# Verbind met de database
conn = sqlite3.connect('../fytotherapie.db')
cursor = conn.cursor()

# Voer het SQL-script uit voor het aanmaken van alle tabellen
cursor.executescript("""

-- Tabel voor planten
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

-- Tussentabel planten-klachten
CREATE TABLE IF NOT EXISTS plant_klacht (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    klacht_id INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES planten(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

-- Klanten en gerelateerde tabellen
CREATE TABLE IF NOT EXISTS klanten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    emailadres TEXT,
    telefoon TEXT,
    adres TEXT
);

CREATE TABLE IF NOT EXISTS notities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    inhoud TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

CREATE TABLE IF NOT EXISTS afspraken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    datumtijd TEXT,
    onderwerp TEXT,
    locatie TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

CREATE TABLE IF NOT EXISTS behandelingen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    naam TEXT,
    datum TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

CREATE TABLE IF NOT EXISTS behandeling_klacht (
    behandeling_id INTEGER,
    klacht_id INTEGER,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

CREATE TABLE IF NOT EXISTS behandeling_plant (
    behandeling_id INTEGER,
    plant_id INTEGER,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (plant_id) REFERENCES planten(id)
);
CREATE TABLE supplementen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    andere_namen TEXT,
    lost_op_in TEXT,
    eigenschap_functie TEXT,
    bij_tekort TEXT,
    inzetten_bij TEXT,
    voedingsbronnen TEXT,
    bijzonderheden TEXT
);


""")


# Voeg planten toe als ze nog niet bestaan
for plant in planten_info:
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant["naam"],))
    result = cursor.fetchone()
    if not result:
        cursor.execute('''
            INSERT INTO planten (
                naam, botanische_naam, beschrijving, te_gebruiken_bij,
                gebruikt_plantendeel, aanbevolen_combinaties, niet_te_gebruiken_bij,
                categorie_kleur, details, afbeelding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            plant["naam"],
            plant["botanische_naam"],
            plant["beschrijving"],
            plant["te_gebruiken_bij"],
            plant["gebruikt_plantendeel"],
            plant["aanbevolen_combinaties"],
            plant["niet_te_gebruiken_bij"],
            plant.get("categorie_kleur", ""),
            plant["details"],
            plant["afbeelding"]
        ))
    else:
        print(f"⏩ Plant '{plant['naam']}' bestaat al, overslaan.")

# Commit & sluit
conn.commit()
conn.close()

print("✅ Planten succesvol toegevoegd aan de database.")
