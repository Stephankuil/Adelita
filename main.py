from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Startpagina
@app.route('/')
def index():
    return render_template('index.html')

# Pagina met alle planten
@app.route('/planten')
def planten():
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM planten ORDER BY naam ASC")
    planten_lijst = cursor.fetchall()
    conn.close()
    return render_template('planten.html', planten=planten_lijst)


@app.route('/klacht/<klacht_naam>')
def klacht_detail(klacht_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Ophalen van ID en gekoppelde planten
    cursor.execute("SELECT id FROM klachten WHERE naam = ?", (klacht_naam,))
    klacht_id_row = cursor.fetchone()
    if not klacht_id_row:
        return f"❌ Klacht '{klacht_naam}' niet gevonden."
    klacht_id = klacht_id_row[0]

    # Huidige koppelingen
    cursor.execute("""
        SELECT planten.naam FROM planten
        JOIN plant_klacht ON planten.id = plant_klacht.plant_id
        WHERE plant_klacht.klacht_id = ?
    """, (klacht_id,))
    gekoppelde_planten = [r[0] for r in cursor.fetchall()]

    # Alle planten (voor dropdown)
    cursor.execute("SELECT id, naam FROM planten ORDER BY naam")
    alle_planten = cursor.fetchall()

    conn.close()

    return render_template("klacht_detail.html", klacht=klacht_naam, gekoppelde_planten=gekoppelde_planten, alle_planten=alle_planten, klacht_id=klacht_id)

@app.route('/klachten')
def klachten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM klachten ORDER BY naam ASC")
    klachten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klachten.html", klachten=klachten_lijst)

@app.route('/verwijder_plant', methods=['POST'])
def verwijder_plant():
    plant_naam = request.form['plant_naam']
    klacht_id = request.form['klacht_id']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal plant_id op via naam
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Plant niet gevonden."
    plant_id = row[0]

    # Verwijder de koppeling
    cursor.execute("DELETE FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?", (plant_id, klacht_id))
    conn.commit()
    conn.close()

    # Redirect terug naar klacht-detail
    cursor = sqlite3.connect("fytotherapie.db").cursor()
    cursor.execute("SELECT naam FROM klachten WHERE id = ?", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]

    return redirect(url_for('klacht_detail', klacht_naam=klacht_naam))


@app.route('/koppel_plant', methods=['POST'])
def koppel_plant():
    klacht_id = request.form['klacht_id']
    plant_id = request.form['plant_id']

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Controleer of de koppeling al bestaat
    cursor.execute("SELECT 1 FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?", (plant_id, klacht_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)", (plant_id, klacht_id))

    conn.commit()
    conn.close()

    # Ophalen van klachtnaam voor redirect
    cursor = sqlite3.connect("fytotherapie.db").cursor()
    cursor.execute("SELECT naam FROM klachten WHERE id = ?", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]
    return redirect(url_for('klacht_detail', klacht_naam=klacht_naam))

if __name__ == '__main__':
    app.run(debug=True)
