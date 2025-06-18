import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Blueprint

# Maak een Blueprint aan voor de klachtenroutes
klacht_bp = Blueprint('klacht_bp', __name__)

# Route voor het tonen van alle klachten
@klacht_bp.route('/klachten')
def klachten():
    # Maak verbinding met de database
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal alle klachten op, gesorteerd op naam
    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()

    # Sluit de databaseverbinding
    conn.close()

    # Geef de klachtenlijst door aan de HTML-template
    return render_template("klachten.html", klachten=klachten_lijst)


# Route voor de detailpagina van een specifieke klacht
@klacht_bp.route('/klacht/<klacht_naam>')
def klacht_detail(klacht_naam):
    # Maak verbinding met de database
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal de ID en beschrijving van de klacht op aan de hand van de naam uit de URL
    cursor.execute("SELECT id, beschrijving FROM klachten WHERE naam = ?", (klacht_naam,))
    klacht_row = cursor.fetchone()

    # Als de klacht niet gevonden is, geef een foutmelding
    if not klacht_row:
        return f"❌ Klacht '{klacht_naam}' niet gevonden."

    # Haal waarden uit de rij
    klacht_id, beschrijving = klacht_row

    # Haal de namen op van alle planten die gekoppeld zijn aan deze klacht
    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = ?
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    # Haal alle planten op voor de dropdown om eventueel te koppelen
    cursor.execute("SELECT id, naam FROM planten ORDER BY LOWER(naam) ASC")
    alle_planten = cursor.fetchall()

    # Sluit de databaseverbinding
    conn.close()

    # Render de detailpagina en geef alle nodige gegevens door
    return render_template(
        "klacht_detail.html",
        klacht=klacht_naam,
        beschrijving=beschrijving,
        gekoppelde_planten=gekoppelde_planten,
        alle_planten=alle_planten,
        klacht_id=klacht_id
    )
