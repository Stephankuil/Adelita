import sqlite3  # Voor communicatie met de SQLite-database
from flask import render_template, Blueprint  # Voor templates en route-structuur (Blueprints)

# Maak een blueprint aan voor routes die met klachten te maken hebben
klacht_bp = Blueprint("klacht_bp", __name__)  # Blueprint met naam 'klacht_bp'

# Route voor het overzicht van alle klachten
@klacht_bp.route("/klachten")
def klachten():
    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de database
    cursor = conn.cursor()  # Maak een cursor voor SQL-queries

    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam ASC")  # Haal alle klachten op, gesorteerd
    klachten_lijst = cursor.fetchall()  # Zet het resultaat in een lijst

    conn.close()  # Sluit de databaseverbinding

    return render_template("klachten.html", klachten=klachten_lijst)  # Render de klachtenpagina met de lijst

# Route voor de detailpagina van een specifieke klacht (inclusief koppel-interface)
@klacht_bp.route("/klacht/<klacht_naam>")
def klacht_detail(klacht_naam):
    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de database
    cursor = conn.cursor()  # Maak een cursor

    cursor.execute("SELECT id, beschrijving FROM klachten WHERE naam = ?", (klacht_naam,))  # Zoek klacht op naam
    klacht_row = cursor.fetchone()  # Haal één resultaat op

    if not klacht_row:  # Als de klacht niet bestaat
        return f"❌ Klacht '{klacht_naam}' niet gevonden."  # Toon foutmelding

    klacht_id, beschrijving = klacht_row  # Haal ID en beschrijving uit de rij

    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = ?
    """, (klacht_id,))  # Haal namen van gekoppelde planten op via JOIN
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]  # Maak lijst van plantennamen

    cursor.execute("SELECT id, naam FROM planten ORDER BY LOWER(naam) ASC")  # Haal alle planten op voor keuzelijst
    alle_planten = cursor.fetchall()  # Resultaat in een lijst

    conn.close()  # Sluit de database

    return render_template(  # Laad de klachten-detailpagina met alle gegevens
        "klacht_detail.html",  # Template-bestand
        klacht=klacht_naam,  # Naam van de klacht
        beschrijving=beschrijving,  # Beschrijving uit de database
        gekoppelde_planten=gekoppelde_planten,  # Alle gekoppelde planten
        alle_planten=alle_planten,  # Alle beschikbare planten
        klacht_id=klacht_id,  # ID van de klacht (voor formulieren)
    )
