import sqlite3
from flask import (

    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

# Definieer een Blueprint voor klantfunctionaliteit
klant_bp = Blueprint("klant_bp", __name__)


# Route om alle klanten weer te geven
@klant_bp.route("/klanten")
def klanten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klanten.html", klanten=klanten_lijst)


# Route om een notitie toe te voegen aan een klant
@klant_bp.route("/klant/<int:klant_id>/notitie_toevoegen", methods=["POST"])  # Route voor het toevoegen van een notitie aan een klant
def notitie_toevoegen(klant_id):  # Functie die wordt aangeroepen bij POST-verzoek op deze route
    inhoud = request.form["inhoud"]  # Haal de inhoud van de notitie op uit het formulier
    conn = sqlite3.connect("fytotherapie.db")  # Maak verbinding met de database
    cursor = conn.cursor()  # Maak een cursor-object voor SQL-bewerkingen

    cursor.execute(  # Voer een SQL-opdracht uit om een nieuwe notitie toe te voegen
        """
        INSERT INTO notities (klant_id, inhoud)  # Voeg klant-ID en notitie-inhoud toe aan notities-tabel
        VALUES (?, ?)
        """,
        (klant_id, inhoud),  # Vervang ? door klant_id en inhoud (voorkomt SQL-injectie)
    )

    conn.commit()  # Sla de wijziging op in de database
    conn.close()  # Sluit de databaseverbinding
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))  # Redirect naar de klantdetailpagina


# Route om een nieuwe behandeling toe te voegen, inclusief koppelen van klachten en planten
@klant_bp.route("/klant/<int:klant_id>/nieuwe_behandeling", methods=["POST"])  # Route om een nieuwe behandeling toe te voegen voor een klant
def nieuwe_behandeling(klant_id):  # Functie die uitgevoerd wordt bij POST-verzoek
    naam = request.form.get("naam")  # Haal de naam van de behandeling op uit het formulier
    datum = request.form.get("datum")  # Haal de datum van de behandeling op
    klacht_ids = request.form.getlist("klachten")  # Haal een lijst van geselecteerde klacht-ID's op
    plant_ids = request.form.getlist("planten")  # Haal een lijst van geselecteerde plant-ID's op

    conn = sqlite3.connect("fytotherapie.db")  # Maak verbinding met de database
    cursor = conn.cursor()  # Maak een cursor-object aan om SQL-commando's uit te voeren

    # Voeg de nieuwe behandeling toe aan de behandelingen-tabel
    cursor.execute(
        "INSERT INTO behandelingen (klant_id, naam, datum) VALUES (?, ?, ?)",  # SQL-query met placeholders
        (klant_id, naam, datum),  # Vervang de placeholders met echte waarden
    )
    behandeling_id = cursor.lastrowid  # Haal het ID op van de net toegevoegde behandeling

    # Voor elke geselecteerde klacht, voeg een relatie toe tussen de behandeling en de klacht
    for klacht_id in klacht_ids:
        cursor.execute(
            "INSERT INTO behandeling_klacht (behandeling_id, klacht_id) VALUES (?, ?)",  # Koppel behandeling aan klacht
            (behandeling_id, klacht_id),
        )

    # Koppel planten aan behandeling
    for plant_id in plant_ids:
        cursor.execute(
            "INSERT INTO behandeling_plant (behandeling_id, plant_id) VALUES (?, ?)",
            (behandeling_id, plant_id),
        )

    conn.commit()
    conn.close()
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))


# (Optioneel) alternatieve route om behandeling op te slaan zonder klachten/planten
@klant_bp.route("/klant/<int:klant_id>/behandeling_toevoegen", methods=["POST"])
def behandeling_toevoegen(klant_id):
    behandeling = request.form.get("behandeling")
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO behandelingen (klant_id, behandeling)
        VALUES (?, ?)
    """,
        (klant_id, behandeling),
    )

    conn.commit()
    conn.close()
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))


# Route om een behandelingstekst te updaten in de klanten-tabel (deprecated model?)
@klant_bp.route("/klant/<int:klant_id>/update_behandeling", methods=["POST"])
def update_behandeling(klant_id):
    behandeling = request.form["behandeling"]
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE klanten SET behandeling = ? WHERE id = ?", (behandeling, klant_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))


# Route om overzicht van klanten en hun laatste behandeling + klachten + planten te tonen
@klant_bp.route("/klanten/behandelingen")  # Route om een overzicht te tonen van klanten en hun laatste behandeling
def klanten_behandelingen():
    conn = sqlite3.connect("fytotherapie.db")  # Maak verbinding met de SQLite database
    cursor = conn.cursor()  # Maak een cursor-object aan voor SQL-queries

    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")  # Haal alle klanten op, gesorteerd op naam
    klanten = cursor.fetchall()  # Zet alle klantresultaten in een lijst

    klant_data = []  # Lege lijst waarin we alle samengevoegde klantgegevens gaan opslaan

    for klant_id, klant_naam in klanten:  # Loop door alle klanten heen
        # Haal de laatste behandeling op (recentste datum) voor deze klant
        cursor.execute(
            """
            SELECT id, naam, datum FROM behandelingen 
            WHERE klant_id = ? ORDER BY datum DESC LIMIT 1
            """,
            (klant_id,),  # Vervang ? door klant_id
        )
        behandeling = cursor.fetchone()  # Haal de eerste (laatste) behandeling op

        if behandeling:  # Als er een behandeling gevonden is
            behandeling_id, behandelingsnaam, datum = behandeling  # Haal gegevens uit de tuple

            # Haal de namen van klachten die gekoppeld zijn aan deze behandeling
            cursor.execute(
                """
                SELECT klachten.naam FROM behandeling_klacht
                JOIN klachten ON behandeling_klacht.klacht_id = klachten.id
                WHERE behandeling_klacht.behandeling_id = ?
                """,
                (behandeling_id,),  # Vervang ? door het ID van de behandeling
            )
            klachten = [row[0] for row in cursor.fetchall()]  # Zet alleen de klacht-namen in een lijst

            # Haal de namen van planten die gekoppeld zijn aan deze behandeling
            cursor.execute(
                """
                SELECT planten.naam FROM behandeling_plant
                JOIN planten ON behandeling_plant.plant_id = planten.id
                WHERE behandeling_plant.behandeling_id = ?
                """,
                (behandeling_id,),  # Vervang ? door behandeling_id
            )
            planten = [row[0] for row in cursor.fetchall()]  # Zet alleen de plant-namen in een lijst
        else:
            behandelingsnaam = ""  # Geen behandeling aanwezig → lege naam
            datum = ""  # Geen datum beschikbaar
            klachten = []  # Geen klachten gekoppeld
            planten = []  # Geen planten gekoppeld

        # Voeg alle info van deze klant toe aan de klant_data lijst
        klant_data.append(
            {
                "id": klant_id,  # ID van de klant
                "naam": klant_naam,  # Naam van de klant
                "behandeling": behandelingsnaam,  # Naam van de laatste behandeling
                "datum": datum,  # Datum van de laatste behandeling
                "klachten": klachten,  # Gekoppelde klachten
                "planten": planten,  # Gekoppelde planten
            }
        )

    conn.close()  # Sluit de databaseverbinding

    return render_template("klanten_behandelingen.html", klanten=klant_data)  # Geef alle gegevens door aan de HTML-template

# Route voor de detailpagina van een klant
@klant_bp.route("/klant/<int:klant_id>")
def klant_detail(klant_id):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal klantgegevens op
    cursor.execute("SELECT * FROM klanten WHERE id = ?", (klant_id,))
    klant = cursor.fetchone()

    # Haal notities op
    cursor.execute(
        "SELECT inhoud, datum FROM notities WHERE klant_id = ? ORDER BY datum DESC",
        (klant_id,),
    )
    notities = cursor.fetchall()

    # Haal afspraken op
    cursor.execute(
        "SELECT datumtijd, onderwerp, locatie FROM afspraken WHERE klant_id = ? ORDER BY datumtijd ASC",
        (klant_id,),
    )
    afspraken = cursor.fetchall()

    # Haal behandelingen op
    cursor.execute(
        "SELECT naam, datum FROM behandelingen WHERE klant_id = ? ORDER BY datum DESC",
        (klant_id,),
    )
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
        planten=planten,
    )


# Route voor het toevoegen van een nieuwe klant
@klant_bp.route("/nieuwe_klant", methods=["POST"])
def nieuwe_klant():
    naam = request.form.get("naam")
    email = request.form.get("emailadres")
    telefoon = request.form.get("telefoon")
    adres = request.form.get("adres")

    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Voeg nieuwe klant toe aan de database
    cursor.execute(
        """
        INSERT INTO klanten (naam, emailadres, telefoon, adres)
        VALUES (?, ?, ?, ?)
    """,
        (naam, email, telefoon, adres),
    )

    klant_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Stuur gebruiker door naar de klant-detailpagina
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))


# Route voor het toevoegen van een nieuwe afspraak aan een klant
@klant_bp.route("/nieuwe_afspraak/<int:klant_id>", methods=["POST"])  # Route om een nieuwe afspraak toe te voegen voor een specifieke klant
def nieuwe_afspraak(klant_id):  # Functie wordt uitgevoerd bij POST-verzoek
    datum = request.form["datum"]  # Haal de datum uit het formulier (bijv. "2025-06-24")
    tijd = request.form["tijd"]  # Haal het tijdstip uit het formulier (bijv. "14:00")
    datumtijd = f"{datum} {tijd}"  # Combineer datum en tijd tot één string (bijv. "2025-06-24 14:00")

    onderwerp = request.form["onderwerp"]  # Haal het onderwerp van de afspraak op
    locatie = request.form["locatie"]  # Haal de locatie van de afspraak op

    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de SQLite database
    cursor = conn.cursor()  # Maak een cursor-object voor het uitvoeren van SQL-queries

    # Voeg de nieuwe afspraak toe aan de database
    cursor.execute(
        """
        INSERT INTO afspraken (klant_id, datumtijd, onderwerp, locatie)
        VALUES (?, ?, ?, ?)  # Voeg klant-ID, datumtijd, onderwerp en locatie toe
        """,
        (klant_id, datumtijd, onderwerp, locatie),  # Vervang de ? met formuliergegevens
    )

    conn.commit()  # Sla de wijzigingen op in de database
    conn.close()  # Sluit de databaseverbinding

    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))  # Stuur gebruiker terug naar de klantdetailpagina
