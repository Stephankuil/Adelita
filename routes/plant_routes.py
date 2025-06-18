from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app
import sqlite3
import os
from werkzeug.utils import secure_filename

# Blueprint voor alles wat met planten te maken heeft
plant_bp = Blueprint('plant_bp', __name__)

# Toegestane bestandsformaten voor afbeeldingen
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Hulpfunctie: check of bestandsnaam een toegestane extensie heeft
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: overzicht van alle planten
@plant_bp.route('/planten')
def planten():
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM planten ORDER BY naam ASC")
    planten_lijst = cursor.fetchall()
    conn.close()
    return render_template('planten.html', planten=planten_lijst)

# Route: toon info van één plant (alleen lezen)
@plant_bp.route('/plant/<plant_naam>/info')
def plant_info(plant_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal plantgegevens op
    cursor.execute("SELECT * FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    kolommen = [col[0] for col in cursor.description]

    if not row:
        conn.close()
        return "Plant niet gevonden."

    plant = dict(zip(kolommen, row))  # Maak dict van kolomnamen en waarden

    # Haal gekoppelde klachten op via plant_id
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    plant_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT klachten.naam FROM klachten
        JOIN plant_klacht ON klachten.id = plant_klacht.klacht_id
        WHERE plant_klacht.plant_id = ?
        ORDER BY klachten.naam
    """, (plant_id,))
    gekoppelde_klachten = [r[0] for r in cursor.fetchall()]

    conn.close()
    return render_template("plant_info.html", plant=plant, gekoppelde_klachten=gekoppelde_klachten)

# Route: detailpagina (bewerken van plant)
@plant_bp.route('/plant/<plant_naam>', methods=['GET', 'POST'])
def plant_detail(plant_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal plant_id op
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    plant_row = cursor.fetchone()
    if not plant_row:
        conn.close()
        return "Plant niet gevonden."
    plant_id = plant_row[0]

    if request.method == 'POST':
        # Formulierdata ophalen
        beschrijving = request.form.get("beschrijving")
        botanische_naam = request.form.get("botanische_naam")
        gebruikt_plantendeel = request.form.get("gebruikt_plantendeel")
        te_gebruiken_bij = request.form.get("te_gebruiken_bij")
        niet_te_gebruiken_bij = request.form.get("niet_te_gebruiken_bij")
        aanbevolen_combinaties = request.form.get("aanbevolen_combinaties")
        details = request.form.get("details")
        geselecteerde_klachten = request.form.getlist("klachten")

        afbeelding_bestandsnaam = None
        if 'afbeelding' in request.files:
            file = request.files['afbeelding']
            if file and allowed_file(file.filename):
                afbeelding_bestandsnaam = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], afbeelding_bestandsnaam))

        # Update plantgegevens in database
        cursor.execute("""
            UPDATE planten
            SET beschrijving = ?, botanische_naam = ?, gebruikt_plantendeel = ?,
                te_gebruiken_bij = ?, niet_te_gebruiken_bij = ?, aanbevolen_combinaties = ?, details = ?,
                afbeelding = COALESCE(?, afbeelding)
            WHERE naam = ?
        """, (
            beschrijving, botanische_naam, gebruikt_plantendeel,
            te_gebruiken_bij, niet_te_gebruiken_bij, aanbevolen_combinaties,
            details, afbeelding_bestandsnaam, plant_naam
        ))

        # Verwijder bestaande klachtkoppelingen en voeg nieuwe toe
        cursor.execute("DELETE FROM plant_klacht WHERE plant_id = ?", (plant_id,))
        for klacht_id in geselecteerde_klachten:
            cursor.execute("INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)", (plant_id, klacht_id))

        conn.commit()

    # Haal plantgegevens opnieuw op voor het formulier
    cursor.execute("SELECT * FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    kolommen = [col[0] for col in cursor.description]
    plant = dict(zip(kolommen, row))

    # Haal alle klachten op voor checkboxen
    cursor.execute("SELECT id, naam FROM klachten ORDER BY naam")
    alle_klachten = cursor.fetchall()
