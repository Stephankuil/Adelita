from flask import render_template, Blueprint
import mysql.connector
from dotenv import load_dotenv
import os
from DB_Config import db_config
load_dotenv()

# Database-configuratie uit .env bestand halen


klacht_bp = Blueprint("klacht_bp", __name__)


def get_db_connection():
    return mysql.connector.connect(**db_config)


# Route voor overzicht van klachten
@klacht_bp.route("/klachten")
def klachten():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("klachten.html", klachten=klachten_lijst)


# Route voor detailpagina van een klacht
@klacht_bp.route("/klacht/<klacht_naam>")
def klacht_detail(klacht_naam):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, beschrijving FROM klachten WHERE naam = %s", (klacht_naam,))
    klacht_row = cursor.fetchone()

    if not klacht_row:
        cursor.close()
        conn.close()
        return f"❌ Klacht '{klacht_naam}' niet gevonden.", 404

    klacht_id, beschrijving = klacht_row

    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = %s
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT id, naam FROM planten ORDER BY naam ASC")
    alle_planten = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "klacht_detail.html",
        klacht=klacht_naam,
        beschrijving=beschrijving,
        gekoppelde_planten=gekoppelde_planten,
        alle_planten=alle_planten,
        klacht_id=klacht_id,
    )
from flask import request, redirect, url_for, flash

@klacht_bp.route("/klacht/toevoegen", methods=["POST"])
def klacht_toevoegen():
    naam = request.form.get("naam")
    beschrijving = request.form.get("beschrijving")

    if not naam or not beschrijving:
        flash("Naam en beschrijving zijn verplicht.")
        return redirect(url_for("klacht_bp.klachten"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO klachten (naam, beschrijving) VALUES (%s, %s)",
            (naam, beschrijving)
        )
        conn.commit()
        flash(f"✅ Klacht '{naam}' succesvol toegevoegd.")
    except mysql.connector.IntegrityError:
        conn.rollback()
        flash(f"⚠️ Klacht '{naam}' bestaat al.")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Fout bij toevoegen: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("klacht_bp.klachten"))

@klacht_bp.route("/klacht/<int:klacht_id>/verwijderen", methods=["POST"])
def klacht_verwijderen(klacht_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # Controleer of de klacht bestaat
        cursor.execute("SELECT naam FROM klachten WHERE id = %s", (klacht_id,))
        result = cursor.fetchone()
        if not result:
            flash("❌ Klacht niet gevonden.")
            return redirect(url_for('klacht_bp.klachten'))

        klacht_naam = result[0]

        # Verwijder eerst alle koppelingen (bijv. met planten of behandelingen)
        cursor.execute("DELETE FROM plant_klacht WHERE klacht_id = %s", (klacht_id,))
        cursor.execute("DELETE FROM behandeling_klacht WHERE klacht_id = %s", (klacht_id,))

        # Verwijder daarna de klacht zelf
        cursor.execute("DELETE FROM klachten WHERE id = %s", (klacht_id,))
        conn.commit()

        flash(f"✅ Klacht '{klacht_naam}' is verwijderd.")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Fout bij verwijderen van klacht: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('klacht_bp.klachten'))

