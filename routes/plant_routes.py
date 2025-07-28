from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
import mysql.connector
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from DB_Config import db_config, get_db_connection
load_dotenv()

# Blueprint aanmaken
plant_bp = Blueprint("plant_bp", __name__)

# Toegestane bestandsextensies
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

conn = get_db_connection()

# ✅ Database connectie-functie
def get_db_connection():
    return mysql.connector.connect(**db_config)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# 📋 Route: alle planten ophalen
@plant_bp.route("/planten")
def planten():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM planten ORDER BY naam ASC")
    planten_lijst = cursor.fetchall()
    conn.close()
    return render_template("planten.html", planten=planten_lijst)

# 📋 Route: plant info
@plant_bp.route("/plant/<plant_naam>/info")
def plant_info(plant_naam):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM planten WHERE naam = %s", (plant_naam,))
    plant = cursor.fetchone()

    if not plant:
        conn.close()
        return "Plant niet gevonden."

    cursor.execute("SELECT id FROM planten WHERE naam = %s", (plant_naam,))
    plant_id = cursor.fetchone()["id"]


    cursor.execute("""
        SELECT klachten.naam FROM klachten
        JOIN plant_klacht ON klachten.id = plant_klacht.klacht_id
        WHERE plant_klacht.plant_id = %s
        ORDER BY klachten.naam
    """, (plant_id,))
    gekoppelde_klachten = [r["naam"] for r in cursor.fetchall()]

    conn.close()
    return render_template("plant_info.html", plant=plant, gekoppelde_klachten=gekoppelde_klachten)

# 📋 Route: plant detail bewerken
@plant_bp.route("/plant/<plant_naam>", methods=["GET", "POST"])
def plant_detail(plant_naam):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM planten WHERE naam = %s", (plant_naam,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return "Plant niet gevonden."
    plant_id = result["id"]

    if request.method == "POST":
        beschrijving = request.form.get("beschrijving")
        botanische_naam = request.form.get("botanische_naam")
        gebruikt_plantendeel = request.form.get("gebruikt_plantendeel")
        te_gebruiken_bij = request.form.get("te_gebruiken_bij")
        niet_te_gebruiken_bij = request.form.get("niet_te_gebruiken_bij")
        aanbevolen_combinaties = request.form.get("aanbevolen_combinaties")
        details = request.form.get("details")
        geselecteerde_klachten = request.form.getlist("klachten")

        afbeelding_bestandsnaam = None
        if "afbeelding" in request.files:
            file = request.files["afbeelding"]
            if file and allowed_file(file.filename):
                afbeelding_bestandsnaam = secure_filename(file.filename)
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], afbeelding_bestandsnaam))

        cursor.execute("""
            UPDATE planten
            SET beschrijving = %s, botanische_naam = %s, gebruikt_plantendeel = %s,
                te_gebruiken_bij = %s, niet_te_gebruiken_bij = %s,
                aanbevolen_combinaties = %s, details = %s,
                afbeelding = COALESCE(%s, afbeelding)
            WHERE naam = %s
        """, (
            beschrijving, botanische_naam, gebruikt_plantendeel,
            te_gebruiken_bij, niet_te_gebruiken_bij,
            aanbevolen_combinaties, details,
            afbeelding_bestandsnaam, plant_naam
        ))

        cursor.execute("DELETE FROM plant_klacht WHERE plant_id = %s", (plant_id,))
        for klacht_id in geselecteerde_klachten:
            cursor.execute("INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (%s, %s)", (plant_id, klacht_id))

        conn.commit()

    cursor.execute("SELECT * FROM planten WHERE naam = %s", (plant_naam,))
    plant = cursor.fetchone()

    cursor.execute("SELECT id, naam FROM klachten ORDER BY naam")
    alle_klachten = cursor.fetchall()

    cursor.execute("SELECT klacht_id FROM plant_klacht WHERE plant_id = %s", (plant_id,))
    gekoppelde_klachten_ids = {row["klacht_id"] for row in cursor.fetchall()}

    conn.close()

    return render_template("plant_detail.html", plant=plant, klachten=alle_klachten, gekoppelde_klachten=gekoppelde_klachten_ids)

# 📋 Route: plant koppelen
@plant_bp.route("/koppel_plant", methods=["POST"])
def koppel_plant():
    klacht_id = request.form["klacht_id"]
    plant_id = request.form["plant_id"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM plant_klacht WHERE plant_id = %s AND klacht_id = %s", (plant_id, klacht_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (%s, %s)", (plant_id, klacht_id))

    cursor.execute("SELECT naam FROM klachten WHERE id = %s", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return redirect(url_for("klacht_bp.klacht_detail", klacht_naam=klacht_naam))

# 📋 Route: plant ontkoppelen
@plant_bp.route("/verwijder_plant", methods=["POST"])
def verwijder_plant():
    plant_naam = request.form["plant_naam"]
    klacht_id = request.form["klacht_id"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM planten WHERE naam = %s", (plant_naam,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Plant niet gevonden."

    plant_id = row[0]
    cursor.execute("DELETE FROM plant_klacht WHERE plant_id = %s AND klacht_id = %s", (plant_id, klacht_id))

    cursor.execute("SELECT naam FROM klachten WHERE id = %s", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return redirect(url_for("klacht_bp.klacht_detail", klacht_naam=klacht_naam))
# ✅ Functie om verbinding te maken


# ✅ Route om nieuwe plant toe te voegen
@plant_bp.route("/plant/toevoegen", methods=["POST"])
def plant_toevoegen():
    data = {
        "naam": request.form.get("naam"),
        "botanische_naam": request.form.get("botanische_naam"),
        "beschrijving": request.form.get("beschrijving"),
        "te_gebruiken_bij": request.form.get("te_gebruiken_bij"),
        "gebruikt_plantendeel": request.form.get("gebruikt_plantendeel"),
        "aanbevolen_combinaties": request.form.get("aanbevolen_combinaties"),
        "niet_te_gebruiken_bij": request.form.get("niet_te_gebruiken_bij"),
        "categorie_kleur": request.form.get("categorie_kleur"),
        "details": request.form.get("details"),
        "afbeelding": request.form.get("afbeelding")
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO planten (
                naam, botanische_naam, beschrijving, te_gebruiken_bij,
                gebruikt_plantendeel, aanbevolen_combinaties, niet_te_gebruiken_bij,
                categorie_kleur, details, afbeelding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(data.values()))
        conn.commit()
        flash(f"✅ Plant '{data['naam']}' toegevoegd.")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Fout bij toevoegen plant: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('plant_bp.planten'))  # Zorg dat deze route bestaat



@plant_bp.route("/plant/<plant_naam>/verwijderen", methods=["POST"])
def plant_verwijderen(plant_naam):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Haal eerst het plant_id op
        cursor.execute("SELECT id FROM planten WHERE naam = %s", (plant_naam,))
        result = cursor.fetchone()
        if not result:
            flash("❌ Plant niet gevonden.")
            return redirect(url_for('plant_bp.planten'))

        plant_id = result[0]

        # Verwijder eventuele koppelingen met klachten
        cursor.execute("DELETE FROM plant_klacht WHERE plant_id = %s", (plant_id,))

        # Verwijder de plant zelf
        cursor.execute("DELETE FROM planten WHERE id = %s", (plant_id,))

        conn.commit()
        flash(f"✅ Plant '{plant_naam}' is verwijderd.")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Fout bij verwijderen: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('plant_bp.planten'))
