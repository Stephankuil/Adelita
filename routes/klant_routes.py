import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, current_app, Blueprint

# Definieer een Blueprint voor klantfunctionaliteit
klant_bp = Blueprint('klant_bp', __name__)

# Route om alle klanten weer te geven
@klant_bp.route('/klanten')
def klanten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klanten.html", klanten=klanten_lijst)

# Route om een notitie toe te voegen aan een klant
@klant_bp.route('/klant/<int:klant_id>/notitie_toevoegen', methods=['POST'])
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
    return redirect(url_for('klant_bp.klant_detail', klant_id=klant_id))

# Route om een nieuwe behandeling toe te voegen, inclusief koppelen van klachten en planten
@klant_bp.route('/klant/<int:klant_id>/nieuwe_behandeling', methods=['POST'])
def nieuwe_behandeling(klant_id):
    naam = request.form.get("naam")
    datum = request.form.get("datum")
    klacht_ids = request.form.getlist("klachten")
    plant_ids = request.form.getlist("planten")

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Voeg behandeling toe
    cursor.execute("INSERT INTO behandelingen (klant_id, naam, datum) VALUES (?, ?, ?)", (klant_id, naam, datum))
    behandeling_id = cursor.lastrowid

    # Koppel klachten aan behandeling
    for klacht_id in klacht_ids:
        cursor.execute("INSERT INTO behandeling_klacht (behandeling_id, klacht_id) VALUES (?, ?)", (behandeling_id, klacht_id))

    # Koppel planten aan behandeling
    for plant_id in plant_ids:
        cursor.execute("INSERT INTO behandeling_plant (behandeling_id, plant_id) VALUES (?, ?)", (behandeling_id, plant_id))

    conn.commit()
    conn.close()
    return redirect(url_for('klant_bp.klant_detail', klant_id=klant_id))

# (Optioneel) alternatieve route om behandeling op te slaan zonder klachten/planten
@klant_bp.route('/klant/<int:klant_id>/behandeling_toevoegen', methods=['POST'])
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
    return redirect(url_for('klant_bp.klant_detail', klant_id=klant_id))

# Route om een behandelingstekst te updaten in de klanten-tabel (deprecated model?)
@klant_bp.route('/klant/<int:klant_id>/update_behandeling', methods=['POST'])
def update_behandeling(klant_id):
    behandeling = request.form['behandeling']
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE klanten SET behandeling = ? WHERE id = ?", (behandeling, klant_id))
    conn.commit()
    conn.close()
    return redirect(url_for('klant_bp.klant_detail', klant_id=klant_id))

# Route om overzicht van klanten en hun laatste behandeling + klachten + planten te tonen
@klant_bp.route('/klanten/behandelingen')
def klanten_behandelingen():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten = cursor.fetchall()

    klant_data = []

    for klant_id, klant_naam in klanten:
        # Haal laatste behandeling op per klant
        cursor.execute("""
            SELECT id, naam, datum FROM behandelingen 
            WHERE klant_id = ? ORDER BY datum DESC LIMIT 1
        """, (klant_id,))
        behandeling = cursor.fetchone()

        if behandeling:
            behandeling_id, behandelingsnaam, datum = behandeling

            # Haal gekoppelde klachten op
            cursor.execute("""
                SELECT klachten.naam FROM behandeling_klacht
                JOIN klachten ON behandeling_klacht.klacht_id = klachten.id
                WHERE behandeling_klacht.behandeling_id = ?
            """, (behandeling_id,))
            klachten = [row[0] for row in cursor.fetchall()]

            # Haal gekoppelde planten op
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

        # Verzamel data per klant
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

# Route voor de detailpagina van een klant
@klant_bp.route('/klant/<int:klant_id>')
def klant_detail(klant_id):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal klantgegevens op
    cursor.execute("SELECT * FROM klanten WHERE id = ?", (klant_id,))
    klant = cursor.fetchone()

    # Haal notities op
    cursor.execute("SELECT inhoud, datum FROM notities WHERE klant_id = ? ORDER BY datum DESC", (klant_id,))
    notities = cursor.fetchall()

    # Haal afspraken op
    cursor.execute("SELECT datumtijd, onderwerp, locatie FROM afspraken WHERE klant_id = ? ORDER BY datumtijd ASC",
                   (klant_id,))
    afspraken = cursor.fetchall()

    # Haal behandelingen op
    cursor.execute("SELECT naam, datum FROM behandelingen WHERE klant_id = ? ORDER BY datum DESC", (klant_id,))
    behandelingen = cursor.fetchall()

    # Haal alle klachten op voor het formulier
    cursor.execute("SELECT id, naam FROM klachten ORDER BY naam")
    klachten = cursor.fetchall()

    # Haal alle planten op voor het formulier
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

# Route voor het toevoegen van een nieuwe klant
@klant_bp.route('/nieuwe_klant', methods=['POST'])
def nieuwe_klant():
    naam = request.form.get('naam')
    email = request.form.get('emailadres')
    telefoon = request.form.get('telefoon')
    adres = request.form.get('adres')

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Voeg nieuwe klant toe aan de database
    cursor.execute("""
        INSERT INTO klanten (naam, emailadres, telefoon, adres)
        VALUES (?, ?, ?, ?)
    """, (naam, email, telefoon, adres))

    klant_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Stuur gebruiker door naar de klant-detailpagina
    return redirect(url_for('klant_bp.klant_detail', klant_id=klant_id))

# Route voor het toevoegen van een nieuwe afspraak aan een klant
@klant_bp.route('/nieuwe_afspraak/<int:klant_id>', methods=['POST'])
def nieuwe_afspraak(klant_id):
    datum = request.form['datum']
    tijd = request.form['tijd']
    datumtijd = f"{datum} {tijd}"

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

    return redirect(url_for('klant_bp.klant_detail', klant_id=klant_id))
