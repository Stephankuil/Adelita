import sqlite3
import pandas as pd

# SQL-scripts
sql_script_1 = """
-- Tabel voor planten
CREATE TABLE IF NOT EXISTS planten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
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
    naam TEXT NOT NULL,
    beschrijving TEXT
);

-- Tussentabel voor relatie tussen planten en klachten
CREATE TABLE IF NOT EXISTS plant_klacht (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    klacht_id INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES planten(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

-- Voeg planten toe
INSERT INTO planten (naam) VALUES 
('Acidophilus'),
('Aloe Vera'),
('Artisjok'),
('Ashwagandha'),
('Avena Sativa'),
('Bacopa'),
('Biergist'),
('Blauwe Bosbesvrucht'),
('Borage-olie'),
('Boswellia'),
('Brandnetel'),
('Canadese Geelwortel'),
('Cat’s Claw'),
('Cranberry'),
('Curcuma'),
('Damiana'),
('Driekleurig Viooltje'),
('Duivelsklauw'),
('Echinacea'),
('Fenegriek'),
('Garcinia'),
('Gember'),
('Ginkgo'),
('Ginseng'),
('Goudpapaver'),
('Griffonia'),
('Groene Thee'),
('Grote Klis'),
('Guarana'),
('Heermoes'),
('Hop'),
('Javaanse Thee'),
('Kersensteel'),
('Konjac'),
('Laksavital'),
('Levertraanolie'),
('Lijnzaadolie'),
('Lithothamnium'),
('Maca'),
('Maretak'),
('Mariadistel'),
('Maté'),
('Meidoorn'),
('Melisse'),
('Moederkruid'),
('Paardenbloem'),
('Passiebloem'),
('Plantaardige Kool'),
('Pompoenpitolie'),
('Propolis'),
('Q10'),
('Reishi – Shiitake – Maitake'),
('Resveratrol'),
('Rhodiola'),
('Rode Gist Rijst'),
('Rode Klaver'),
('Royal Jelly'),
('Russische Ginseng'),
('Saffraan'),
('Salvia'),
('Sint Janskruid'),
('Spirulina'),
('Teunisbloemolie'),
('Valeriaan'),
('Venkel'),
('Vitamine D3 (plantaardig)'),
('Vrouwenmantel'),
('Weegbree'),
('Zaagbladpalm');
"""

sql_script_2 = """
-- Tabel voor klanten
CREATE TABLE IF NOT EXISTS klanten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    emailadres TEXT,
    telefoon TEXT,
    adres TEXT
);

-- Tabel voor notities per klant
CREATE TABLE IF NOT EXISTS notities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    inhoud TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

-- Tabel voor afspraken
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

"""

# ✅ Alles in één nette transactie
with sqlite3.connect("fytotherapie.db") as conn:
    cursor = conn.cursor()

    # Voer SQL-scripts uit
    cursor.executescript(sql_script_1)
    cursor.executescript(sql_script_2)

    print("Database en tabellen aangemaakt ✅")

    # Klachten uit CSV importeren
    df = pd.read_csv("klachtenlijst.csv")

    for klacht in df['klacht']:
        cursor.execute("INSERT INTO klachten (naam) VALUES (?)", (klacht,))

    print("✅ Klachten succesvol geïmporteerd in de database.")


conn.commit()
conn.close()