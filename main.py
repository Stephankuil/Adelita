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
    cursor.execute("SELECT id, naam, beschrijving FROM klachten ORDER BY naam")
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


@app.route('/klanten')
def klanten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klanten.html", klanten=klanten_lijst)

@app.route('/klant/<int:klant_id>/notitie_toevoegen', methods=['POST'])
def notitie_toevoegen(klant_id):
    inhoud = request.form['inhoud']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notities (klant_id, inhoud)
        VALUES (?, ?)
    """, (klant_id, inhoud))

    conn.commit()
    conn.close()

    return redirect(url_for('klant_detail', klant_id=klant_id))

@app.route('/klant/<int:klant_id>/nieuwe_behandeling', methods=['POST'])
def nieuwe_behandeling(klant_id):
    naam = request.form.get("naam")
    datum = request.form.get("datum")
    klacht_ids = request.form.getlist("klachten")
    plant_ids = request.form.getlist("planten")

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO behandelingen (klant_id, naam, datum) VALUES (?, ?, ?)", (klant_id, naam, datum))
    behandeling_id = cursor.lastrowid

    for klacht_id in klacht_ids:
        cursor.execute("INSERT INTO behandeling_klacht (behandeling_id, klacht_id) VALUES (?, ?)", (behandeling_id, klacht_id))

    for plant_id in plant_ids:
        cursor.execute("INSERT INTO behandeling_plant (behandeling_id, plant_id) VALUES (?, ?)", (behandeling_id, plant_id))

    conn.commit()
    conn.close()

    return redirect(url_for('klant_detail', klant_id=klant_id))


@app.route('/klant/<int:klant_id>/behandeling_toevoegen', methods=['POST'])
def behandeling_toevoegen(klant_id):
    behandeling = request.form.get('behandeling')

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO behandelingen (klant_id, behandeling)
        VALUES (?, ?)
    """, (klant_id, behandeling))

    conn.commit()
    conn.close()

    return redirect(url_for('klant_detail', klant_id=klant_id))

@app.route('/klant/<int:klant_id>/update_behandeling', methods=['POST'])
def update_behandeling(klant_id):
    behandeling = request.form['behandeling']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE klanten SET behandeling = ? WHERE id = ?", (behandeling, klant_id))
    conn.commit()
    conn.close()

    return redirect(url_for('klant_detail', klant_id=klant_id))

@app.route('/klanten/behandelingen')
def klanten_behandelingen():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal klanten op
    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten = cursor.fetchall()

    klant_data = []

    for klant_id, klant_naam in klanten:
        # Laatste behandeling van deze klant
        cursor.execute("""
            SELECT id, naam, datum FROM behandelingen 
            WHERE klant_id = ? ORDER BY datum DESC LIMIT 1
        """, (klant_id,))
        behandeling = cursor.fetchone()

        if behandeling:
            behandeling_id, behandelingsnaam, datum = behandeling

            # Klachten voor deze behandeling
            cursor.execute("""
                SELECT klachten.naam FROM behandeling_klacht
                JOIN klachten ON behandeling_klacht.klacht_id = klachten.id
                WHERE behandeling_klacht.behandeling_id = ?
            """, (behandeling_id,))
            klachten = [row[0] for row in cursor.fetchall()]

            # Planten voor deze behandeling
            cursor.execute("""
                SELECT planten.naam FROM behandeling_plant
                JOIN planten ON behandeling_plant.plant_id = planten.id
                WHERE behandeling_plant.behandeling_id = ?
            """, (behandeling_id,))
            planten = [row[0] for row in cursor.fetchall()]
        else:
            behandelingsnaam = ""
            datum = ""
            klachten = []
            planten = []

        klant_data.append({
            'id': klant_id,
            'naam': klant_naam,
            'behandeling': behandelingsnaam,
            'datum': datum,
            'klachten': klachten,
            'planten': planten
        })

    conn.close()
    return render_template("klanten_behandelingen.html", klanten=klant_data)

@app.route('/klant/<int:klant_id>')
def klant_detail(klant_id):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Klantgegevens
    cursor.execute("SELECT * FROM klanten WHERE id = ?", (klant_id,))
    klant = cursor.fetchone()

    # Notities ophalen
    cursor.execute("SELECT inhoud, datum FROM notities WHERE klant_id = ? ORDER BY datum DESC", (klant_id,))
    notities = cursor.fetchall()

    # Afspraken ophalen
    cursor.execute("SELECT datumtijd, onderwerp FROM afspraken WHERE klant_id = ? ORDER BY datumtijd ASC", (klant_id,))
    afspraken = cursor.fetchall()

    # Behandelingen ophalen
    cursor.execute("SELECT naam, datum FROM behandelingen WHERE klant_id = ? ORDER BY datum DESC", (klant_id,))
    behandelingen = cursor.fetchall()

    # Klachten ophalen (voor formulier)
    cursor.execute("SELECT id, naam FROM klachten ORDER BY naam")
    klachten = cursor.fetchall()

    # Planten ophalen (voor formulier)
    cursor.execute("SELECT id, naam FROM planten ORDER BY naam")
    planten = cursor.fetchall()

    conn.close()
    return render_template(
        "klant_detail.html",
        klant=klant,
        notities=notities,
        afspraken=afspraken,
        behandelingen=behandelingen,
        klachten=klachten,
        planten=planten
    )


@app.route('/nieuwe_klant', methods=['POST'])
def nieuwe_klant():
    naam = request.form.get('naam')
    email = request.form.get('emailadres')
    telefoon = request.form.get('telefoon')
    adres = request.form.get('adres')

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Voeg klant toe
    cursor.execute("""
        INSERT INTO klanten (naam, emailadres, telefoon, adres)
        VALUES (?, ?, ?, ?)
    """, (naam, email, telefoon, adres))

    # Haal het ID van de nieuwe klant op
    klant_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Stuur direct door naar de detailpagina
    return redirect(url_for('klant_detail', klant_id=klant_id))

@app.route('/nieuwe_afspraak/<int:klant_id>', methods=['POST'])
def nieuwe_afspraak(klant_id):
    datum = request.form['datum']           # bijv. "2025-04-23"
    tijd = request.form['tijd']             # bijv. "14:30"
    datumtijd = f"{datum} {tijd}"           # gecombineerd

    onderwerp = request.form['onderwerp']
    locatie = request.form['locatie']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO afspraken (klant_id, datumtijd, onderwerp, locatie)
        VALUES (?, ?, ?, ?)
    """, (klant_id, datumtijd, onderwerp, locatie))

    conn.commit()
    conn.close()

    return redirect(url_for('klant_detail', klant_id=klant_id))


if __name__ == '__main__':
    app.run(debug=True)
