from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Startpagina
@app.route('/')
def index():
    return render_template('index.html')

# Alle planten
@app.route('/planten')
def planten():
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM planten ORDER BY naam ASC")
    planten_lijst = cursor.fetchall()
    conn.close()
    return render_template('planten.html', planten=planten_lijst)

# Plant detail + bewerken
@app.route('/plant/<plant_naam>', methods=['GET', 'POST'])
def plant_detail(plant_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        beschrijving = request.form.get("beschrijving")
        botanische_naam = request.form.get("botanische_naam")
        gebruikt_plantendeel = request.form.get("gebruikt_plantendeel")
        te_gebruiken_bij = request.form.get("te_gebruiken_bij")
        niet_te_gebruiken_bij = request.form.get("niet_te_gebruiken_bij")
        aanbevolen_combinaties = request.form.get("aanbevolen_combinaties")
        details = request.form.get("details")

        afbeelding_bestandsnaam = None
        if 'afbeelding' in request.files:
            file = request.files['afbeelding']
            if file and allowed_file(file.filename):
                afbeelding_bestandsnaam = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], afbeelding_bestandsnaam))

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
        conn.commit()

    # Gegevens ophalen
    cursor.execute("SELECT * FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    kolommen = [col[0] for col in cursor.description]
    conn.close()

    if not row:
        return "Plant niet gevonden."

    plant = dict(zip(kolommen, row))
    return render_template("plant_detail.html", plant=plant)

# Alle klachten
@app.route('/klachten')
def klachten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klachten.html", klachten=klachten_lijst)

# Detailpagina klacht + koppel UI
@app.route('/klacht/<klacht_naam>')
def klacht_detail(klacht_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM klachten WHERE naam = ?", (klacht_naam,))
    klacht_id_row = cursor.fetchone()
    if not klacht_id_row:
        return f"❌ Klacht '{klacht_naam}' niet gevonden."
    klacht_id = klacht_id_row[0]

    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = ?
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT id, naam FROM planten ORDER BY naam")
    alle_planten = cursor.fetchall()
    conn.close()

    return render_template("klacht_detail.html", klacht=klacht_naam, gekoppelde_planten=gekoppelde_planten, alle_planten=alle_planten, klacht_id=klacht_id)

# Koppel plant aan klacht
@app.route('/koppel_plant', methods=['POST'])
def koppel_plant():
    klacht_id = request.form['klacht_id']
    plant_id = request.form['plant_id']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?", (plant_id, klacht_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)", (plant_id, klacht_id))
    conn.commit()
    cursor.execute("SELECT naam FROM klachten WHERE id = ?", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]
    conn.close()
    return redirect(url_for('klacht_detail', klacht_naam=klacht_naam))

# Verwijder koppeling plant-klacht
@app.route('/verwijder_plant', methods=['POST'])
def verwijder_plant():
    plant_naam = request.form['plant_naam']
    klacht_id = request.form['klacht_id']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Plant niet gevonden."
    plant_id = row[0]
    cursor.execute("DELETE FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?", (plant_id, klacht_id))
    conn.commit()

    cursor.execute("SELECT naam FROM klachten WHERE id = ?", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]
    conn.close()
    return redirect(url_for('klacht_detail', klacht_naam=klacht_naam))

if __name__ == '__main__':
    app.run(debug=True)
