from flask import render_template, Blueprint
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Database-configuratie uit .env bestand halen
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

klacht_bp = Blueprint("klacht_bp", __name__)

# Route voor overzicht van klachten
@klacht_bp.route("/klachten")
def klachten():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()

    conn.close()
    return render_template("klachten.html", klachten=klachten_lijst)

# Route voor detailpagina van een klacht
@klacht_bp.route("/klacht/<klacht_naam>")
def klacht_detail(klacht_naam):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT id, beschrijving FROM klachten WHERE naam = %s", (klacht_naam,))
    klacht_row = cursor.fetchone()

    if not klacht_row:
        return f"❌ Klacht '{klacht_naam}' niet gevonden."

    klacht_id, beschrijving = klacht_row

    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = %s
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT id, naam FROM planten ORDER BY LOWER(naam) ASC")
    alle_planten = cursor.fetchall()

    conn.close()

    return render_template(
        "klacht_detail.html",
        klacht=klacht_naam,
        beschrijving=beschrijving,
        gekoppelde_planten=gekoppelde_planten,
        alle_planten=alle_planten,
        klacht_id=klacht_id,
    )
