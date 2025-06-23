from flask import Blueprint, render_template, request, redirect, url_for
from flask import current_app
import sqlite3
import os
from werkzeug.utils import secure_filename

# Blueprint aanmaken voor routes die met planten te maken hebben
plant_bp = Blueprint("plant_bp", __name__)

# Toegestane bestandsextensies voor afbeeldingen
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# Controleer of een bestand een toegestane extensie heeft
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Route om alle planten alfabetisch op te halen en weer te geven
@plant_bp.route("/planten")
def planten():
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM planten ORDER BY naam ASC")
    planten_lijst = cursor.fetchall()
    conn.close()
    return render_template("planten.html", planten=planten_lijst)


# Route om informatie van een specifieke plant op te halen en weer te geven
@plant_bp.route("/plant/<plant_naam>/info")
def plant_info(plant_naam):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal alle kolommen op van de plant
    cursor.execute("SELECT * FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    kolommen = [col[0] for col in cursor.description]

    # Als plant niet bestaat, toon foutmelding
    if not row:
        conn.close()
        return "Plant niet gevonden."

    # Zet rijen en kolommen samen tot dictionary
    plant = dict(zip(kolommen, row))

    # Haal het plant_id op om klachten te koppelen
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    plant_id = cursor.fetchone()[0]

    # Haal alle gekoppelde klachten op voor deze plant
    cursor.execute(
        """
        SELECT klachten.naam FROM klachten
        JOIN plant_klacht ON klachten.id = plant_klacht.klacht_id
        WHERE plant_klacht.plant_id = ?
        ORDER BY klachten.naam
    """,
        (plant_id,),
    )
    gekoppelde_klachten = [r[0] for r in cursor.fetchall()]

    conn.close()
    return render_template(
        "plant_info.html", plant=plant, gekoppelde_klachten=gekoppelde_klachten
    )


# Route om plantdetails te bekijken en te bewerken
@plant_bp.route("/plant/<plant_naam>", methods=["GET", "POST"])  # Route om plantdetails te bekijken of te bewerken
def plant_detail(plant_naam):
    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de database
    cursor = conn.cursor()  # Maak een cursor-object

    # Zoek de ID van de plant op basis van de naam
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    plant_row = cursor.fetchone()
    if not plant_row:  # Als de plant niet bestaat
        conn.close()
        return "Plant niet gevonden."  # Geef foutmelding terug
    plant_id = plant_row[0]  # Haal plant-ID uit resultaat

    if request.method == "POST":  # Als er een formulier is ingestuurd
        beschrijving = request.form.get("beschrijving")  # Haal beschrijving op
        botanische_naam = request.form.get("botanische_naam")  # Botanische naam
        gebruikt_plantendeel = request.form.get("gebruikt_plantendeel")  # Gebruikt deel
        te_gebruiken_bij = request.form.get("te_gebruiken_bij")  # Indicaties
        niet_te_gebruiken_bij = request.form.get("niet_te_gebruiken_bij")  # Contra-indicaties
        aanbevolen_combinaties = request.form.get("aanbevolen_combinaties")  # Combinaties
        details = request.form.get("details")  # Extra details
        geselecteerde_klachten = request.form.getlist("klachten")  # Geselecteerde klachten

        afbeelding_bestandsnaam = None  # Standaard geen afbeelding
        if "afbeelding" in request.files:  # Check of afbeelding aanwezig is
            file = request.files["afbeelding"]
            if file and allowed_file(file.filename):  # Check bestandstype
                afbeelding_bestandsnaam = secure_filename(file.filename)  # Maak bestandsnaam veilig
                file.save(  # Sla bestand op
                    os.path.join(
                        current_app.config["UPLOAD_FOLDER"], afbeelding_bestandsnaam
                    )
                )

        # Update de plantgegevens in de database
        cursor.execute(
            """
            UPDATE planten
            SET beschrijving = ?, botanische_naam = ?, gebruikt_plantendeel = ?,
                te_gebruiken_bij = ?, niet_te_gebruiken_bij = ?, aanbevolen_combinaties = ?, details = ?,
                afbeelding = COALESCE(?, afbeelding)  -- Gebruik nieuwe afbeelding als aanwezig
            WHERE naam = ?
            """,
            (
                beschrijving,
                botanische_naam,
                gebruikt_plantendeel,
                te_gebruiken_bij,
                niet_te_gebruiken_bij,
                aanbevolen_combinaties,
                details,
                afbeelding_bestandsnaam,
                plant_naam,
            ),
        )

        cursor.execute("DELETE FROM plant_klacht WHERE plant_id = ?", (plant_id,))  # Verwijder oude koppelingen

        # Voeg nieuwe koppelingen toe met geselecteerde klachten
        for klacht_id in geselecteerde_klachten:
            cursor.execute(
                "INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)",
                (plant_id, klacht_id),
            )

        conn.commit()  # Sla alle wijzigingen op

    # Haal plantgegevens opnieuw op (ook bij GET-verzoek)
    cursor.execute("SELECT * FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()
    kolommen = [col[0] for col in cursor.description]  # Haal kolomnamen op
    plant = dict(zip(kolommen, row))  # Maak dictionary van kolommen en waarden

    cursor.execute("SELECT id, naam FROM klachten ORDER BY naam")  # Haal alle klachten op
    alle_klachten = cursor.fetchall()

    cursor.execute("SELECT klacht_id FROM plant_klacht WHERE plant_id = ?", (plant_id,))  # Haal gekoppelde klachten op
    gekoppelde_klachten_ids = {row[0] for row in cursor.fetchall()}  # Zet in een set

    conn.close()  # Sluit de databaseverbinding

    # Render de plant detail template met alle gegevens
    return render_template(
        "plant_detail.html",
        plant=plant,
        klachten=alle_klachten,
        gekoppelde_klachten=gekoppelde_klachten_ids,
    )



# Route om een plant te koppelen aan een klacht
@plant_bp.route("/koppel_plant", methods=["POST"])  # Route om een plant te koppelen aan een klacht via een POST-verzoek
def koppel_plant():
    klacht_id = request.form["klacht_id"]  # Haal de klacht-ID op uit het formulier
    plant_id = request.form["plant_id"]  # Haal de plant-ID op uit het formulier

    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de SQLite database
    cursor = conn.cursor()  # Maak een cursor-object voor SQL-queries

    # Controleer of de koppeling tussen deze plant en klacht al bestaat
    cursor.execute(
        "SELECT 1 FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?",  # Zoek naar bestaande koppeling
        (plant_id, klacht_id),  # Vervang de ? met plant_id en klacht_id
    )
    if not cursor.fetchone():  # Als er geen bestaande koppeling is gevonden...
        # Voeg de koppeling toe aan de tabel plant_klacht
        cursor.execute(
            "INSERT INTO plant_klacht (plant_id, klacht_id) VALUES (?, ?)",  # Voeg nieuwe koppeling toe
            (plant_id, klacht_id),
        )

    conn.commit()  # Sla de wijziging op in de database

    # Haal de naam van de klacht op zodat we terug kunnen linken naar de juiste detailpagina
    cursor.execute("SELECT naam FROM klachten WHERE id = ?", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]  # Haal de klachtnaam uit de queryresultaten

    conn.close()  # Sluit de databaseverbinding

    return redirect(url_for("klacht_bp.klacht_detail", klacht_naam=klacht_naam))  # Redirect naar de klacht-detailpagina

# Route om een koppeling tussen plant en klacht te verwijderen
@plant_bp.route("/verwijder_plant", methods=["POST"])  # Route voor het verwijderen van een plant-koppeling via POST
def verwijder_plant():
    plant_naam = request.form["plant_naam"]  # Haal de plantnaam op uit het formulier
    klacht_id = request.form["klacht_id"]  # Haal de klacht-ID op uit het formulier

    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de SQLite database
    cursor = conn.cursor()  # Maak een cursor-object voor SQL-queries

    # Zoek het plant-ID op aan de hand van de naam
    cursor.execute("SELECT id FROM planten WHERE naam = ?", (plant_naam,))
    row = cursor.fetchone()  # Haal het eerste resultaat op

    if not row:  # Als de plant niet bestaat
        conn.close()  # Sluit de verbinding
        return "Plant niet gevonden."  # Geef een foutmelding terug

    plant_id = row[0]  # Haal het ID uit de resultaat-tuple

    # Verwijder de koppeling tussen plant en klacht uit de koppeltabel
    cursor.execute(
        "DELETE FROM plant_klacht WHERE plant_id = ? AND klacht_id = ?",  # SQL DELETE-opdracht
        (plant_id, klacht_id),  # Vervang ? met respectievelijk plant_id en klacht_id
    )
    conn.commit()  # Sla de wijziging op

    # Haal de naam van de klacht op zodat we kunnen redirecten naar de juiste pagina
    cursor.execute("SELECT naam FROM klachten WHERE id = ?", (klacht_id,))
    klacht_naam = cursor.fetchone()[0]  # Haal de klachtnaam uit het resultaat

    conn.close()  # Sluit de databaseverbinding

    return redirect(url_for("klacht_bp.klacht_detail", klacht_naam=klacht_naam))  # Redirect naar de klacht-detailpagina
