import sqlite3
from flask import Flask, render_template, request, redirect, url_for, Blueprint


klacht_bp = Blueprint('klacht_bp', __name__)
@klacht_bp.route('/klachten')
def klachten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klachten.html", klachten=klachten_lijst)

# Detailpagina klacht + koppel UI
@klacht_bp.route('/klacht/<klacht_naam>')
def klacht_detail(klacht_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal klachtgegevens op
    cursor.execute("SELECT id, beschrijving FROM klachten WHERE naam = ?", (klacht_naam,))
    klacht_row = cursor.fetchone()
    if not klacht_row:
        return f"❌ Klacht '{klacht_naam}' niet gevonden."

    klacht_id, beschrijving = klacht_row

    # Haal gekoppelde planten op
    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = ?
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    # Haal alle planten op voor eventueel koppelen
    cursor.execute("SELECT id, naam FROM planten ORDER BY LOWER(naam) ASC")
    alle_planten = cursor.fetchall()

    conn.close()

    return render_template(
        "klacht_detail.html",
        klacht=klacht_naam,
        beschrijving=beschrijving,
        gekoppelde_planten=gekoppelde_planten,
        alle_planten=alle_planten,
        klacht_id=klacht_id
    )

