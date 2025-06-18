import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Blueprint

# Maak een blueprint aan voor routes die met klachten te maken hebben
klacht_bp = Blueprint('klacht_bp', __name__)


# Route voor het overzicht van alle klachten
@klacht_bp.route('/klachten')
def klachten():
    # Verbind met de database
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal id, naam en beschrijving van alle klachten op, alfabetisch gesorteerd
    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()

    # Sluit de databaseverbinding
    conn.close()

    # Render de klachten.html-template met de opgehaalde klachten
    return render_template("klachten.html", klachten=klachten_lijst)


# Route voor de detailpagina van een specifieke klacht (inclusief koppel-interface)
@klacht_bp.route('/klacht/<klacht_naam>')
def klacht_detail(klacht_naam):
    # Verbind met de database
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal het ID en de beschrijving op van de opgegeven klacht
    cursor.execute("SELECT id, beschrijving FROM klachten WHERE naam = ?", (klacht_naam,))
    klacht_row = cursor.fetchone()

    # Als de klacht niet bestaat, geef een foutmelding terug
    if not klacht_row:
        return f"❌ Klacht '{klacht_naam}' niet gevonden."

    # Haal het ID en de beschrijving uit de resultaat-row
    klacht_id, beschrijving = klacht_row

    # Haal de namen op van alle planten die gekoppeld zijn aan deze klacht
    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = ?
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    # Haal alle planten op (voor het tonen van een keuzelijst om te koppelen)
    cursor.execute("SELECT id, naam FROM planten ORDER BY LOWER(naam) ASC")
    alle_planten = cursor.fetchall()

    # Sluit de databaseverbinding
    conn.close()

    # Render de detailpagina met alle opgehaalde gegevens
    return render_template(
        "klacht_detail.html",  # Template voor klachten-detail
        klacht=klacht_naam,  # Naam van de klacht
        beschrijving=beschrijving,  # Beschrijving van de klacht
        gekoppelde_planten=gekoppelde_planten,  # Lijst met gekoppelde planten
        alle_planten=alle_planten,  # Alle beschikbare planten
        klacht_id=klacht_id  # ID van de klacht (nodig voor formulieren)
    )
