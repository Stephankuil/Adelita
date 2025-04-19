import sqlite3

# Verbind met database (maakt het bestand aan als het nog niet bestaat)
conn = sqlite3.connect("fytotherapie.db")
cursor = conn.cursor()

# SQL-commando’s
sql_script = """
-- Tabel voor planten
CREATE TABLE IF NOT EXISTS planten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    botanische_naam TEXT,
    beschrijving TEXT,
    gebruikt_plantendeel TEXT,
    aanbevolen_combinaties TEXT,
    niet_te_gebruiken_bij TEXT,
    categorie_kleur TEXT
);

-- Tabel voor klachten
CREATE TABLE IF NOT EXISTS klachten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL
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

# Script uitvoeren
cursor.executescript(sql_script)

# Opslaan en afsluiten
conn.commit()
conn.close()

print("Database aangemaakt en gevuld ✅")

import pandas as pd

# CSV-bestand inlezen
df = pd.read_csv("klachtenlijst.csv")

# Verbinden met SQLite-database
conn = sqlite3.connect("fytotherapie.db")
cursor = conn.cursor()

# Klachten invoegen in de database
for klacht in df['klacht']:
    cursor.execute("INSERT INTO klachten (naam) VALUES (?)", (klacht,))

# Opslaan en afsluiten
conn.commit()
conn.close()

print("✅ Klachten succesvol geïmporteerd in de database.")