import mysql.connector
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    flash
)
from dotenv import load_dotenv
import os

# Laad omgevingsvariabelen
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Definieer een Blueprint voor klantfunctionaliteit
klant_bp = Blueprint("klant_bp", __name__)

# Databaseconfiguratie uit .env
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)



@klant_bp.route("/klanten")
def klanten():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten_lijst = cursor.fetchall()
    conn.close()
    return render_template("klanten.html", klanten=klanten_lijst)

# Route om een notitie toe te voegen aan een klant
@klant_bp.route("/klant/<int:klant_id>/notitie_toevoegen", methods=["POST"])
def notitie_toevoegen(klant_id):
    inhoud = request.form["inhoud"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO notities (klant_id, inhoud)
        VALUES (%s, %s)
        """,
        (klant_id, inhoud),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))

# Route om een nieuwe behandeling toe te voegen, inclusief koppelen van klachten en planten
@klant_bp.route("/klant/<int:klant_id>/nieuwe_behandeling", methods=["POST"])
def nieuwe_behandeling(klant_id):
    naam = request.form.get("naam")
    datum = request.form.get("datum")
    klacht_ids = request.form.getlist("klachten")
    plant_ids = request.form.getlist("planten")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO behandelingen (klant_id, naam, datum) VALUES (%s, %s, %s)",
        (klant_id, naam, datum),
    )
    behandeling_id = cursor.lastrowid

    for klacht_id in klacht_ids:
        cursor.execute(
            "INSERT INTO behandeling_klacht (behandeling_id, klacht_id) VALUES (%s, %s)",
            (behandeling_id, klacht_id),
        )

    for plant_id in plant_ids:
        cursor.execute(
            "INSERT INTO behandeling_plant (behandeling_id, plant_id) VALUES (%s, %s)",
            (behandeling_id, plant_id),
        )

    conn.commit()
    conn.close()
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))



# Alternatieve route om behandeling op te slaan zonder klachten/planten
@klant_bp.route("/klant/<int:klant_id>/behandeling_toevoegen", methods=["POST"])
def behandeling_toevoegen(klant_id):
    behandeling = request.form.get("behandeling")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO behandelingen (klant_id, behandeling)
        VALUES (%s, %s)
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE klanten SET behandeling = %s WHERE id = %s", (behandeling, klant_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))


# Route om overzicht van klanten en hun laatste behandeling + klachten + planten te tonen
@klant_bp.route("/klanten/behandelingen")
def klanten_behandelingen():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, naam FROM klanten ORDER BY naam")
    klanten = cursor.fetchall()

    klant_data = []

    for klant_id, klant_naam in klanten:
        # Haal de laatste behandeling op
        cursor.execute(
            """
            SELECT id, naam, datum FROM behandelingen 
            WHERE klant_id = %s ORDER BY datum DESC LIMIT 1
            """,
            (klant_id,),
        )
        behandeling = cursor.fetchone()

        if behandeling:
            behandeling_id, behandelingsnaam, datum = behandeling

            # Klachten ophalen
            cursor.execute(
                """
                SELECT klachten.naam FROM behandeling_klacht
                JOIN klachten ON behandeling_klacht.klacht_id = klachten.id
                WHERE behandeling_klacht.behandeling_id = %s
                """,
                (behandeling_id,),
            )
            klachten = [row[0] for row in cursor.fetchall()]

            # Planten ophalen
            cursor.execute(
                """
                SELECT planten.naam FROM behandeling_plant
                JOIN planten ON behandeling_plant.plant_id = planten.id
                WHERE behandeling_plant.behandeling_id = %s
                """,
                (behandeling_id,),
            )
            planten = [row[0] for row in cursor.fetchall()]
        else:
            behandelingsnaam = ""
            datum = ""
            klachten = []
            planten = []

        klant_data.append(
            {
                "id": klant_id,
                "naam": klant_naam,
                "behandeling": behandelingsnaam,
                "datum": datum,
                "klachten": klachten,
                "planten": planten,
            }
        )

    conn.close()
    return render_template("klanten_behandelingen.html", klanten=klant_data)
@klant_bp.route("/klant/<int:klant_id>")
def klant_detail(klant_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM klanten WHERE id = %s", (klant_id,))
    klant = cursor.fetchone()

    cursor.execute(
        "SELECT inhoud, datum FROM notities WHERE klant_id = %s ORDER BY datum DESC",
        (klant_id,),
    )
    notities = cursor.fetchall()

    cursor.execute(
        "SELECT datumtijd, onderwerp, locatie FROM afspraken WHERE klant_id = %s ORDER BY datumtijd ASC",
        (klant_id,),
    )
    afspraken = cursor.fetchall()

    cursor.execute(
        "SELECT naam, datum FROM behandelingen WHERE klant_id = %s ORDER BY datum DESC",
        (klant_id,),
    )
    behandelingen = cursor.fetchall()

    cursor.execute("SELECT id, naam FROM klachten ORDER BY naam")
    klachten = cursor.fetchall()

    cursor.execute("SELECT id, naam FROM planten ORDER BY naam")
    planten = cursor.fetchall()

    cursor.close()
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


@klant_bp.route("/nieuwe_klant", methods=["POST"])
def nieuwe_klant():
    naam = request.form.get("naam")
    email = request.form.get("emailadres")
    telefoon = request.form.get("telefoon")
    adres = request.form.get("adres")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO klanten (naam, emailadres, telefoon, adres)
        VALUES (%s, %s, %s, %s)
        """,
        (naam, email, telefoon, adres),
    )

    klant_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))

@klant_bp.route("/nieuwe_afspraak/<int:klant_id>", methods=["POST"])
def nieuwe_afspraak(klant_id):
    datum = request.form["datum"]
    tijd = request.form["tijd"]
    datumtijd = f"{datum} {tijd}"

    onderwerp = request.form["onderwerp"]
    locatie = request.form["locatie"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO afspraken (klant_id, datumtijd, onderwerp, locatie)
        VALUES (%s, %s, %s, %s)
        """,
        (klant_id, datumtijd, onderwerp, locatie),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("klant_bp.klant_detail", klant_id=klant_id))

@klant_bp.route("/klant/<int:klant_id>/verwijderen", methods=["POST"])
def klant_verwijderen(klant_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Stap 1: Verwijder gekoppelde behandeling_plant en behandeling_klacht via behandeling_id
        cursor.execute("SELECT id FROM behandelingen WHERE klant_id = %s", (klant_id,))
        behandeling_ids = [row[0] for row in cursor.fetchall()]

        for behandeling_id in behandeling_ids:
            cursor.execute("DELETE FROM behandeling_plant WHERE behandeling_id = %s", (behandeling_id,))
            cursor.execute("DELETE FROM behandeling_klacht WHERE behandeling_id = %s", (behandeling_id,))

        # Stap 2: Verwijder behandelingen zelf
        cursor.execute("DELETE FROM behandelingen WHERE klant_id = %s", (klant_id,))

        # Stap 3: Verwijder afspraken
        cursor.execute("DELETE FROM afspraken WHERE klant_id = %s", (klant_id,))

        # Stap 4: Verwijder notities
        cursor.execute("DELETE FROM notities WHERE klant_id = %s", (klant_id,))

        # Stap 5: Verwijder klant
        cursor.execute("DELETE FROM klanten WHERE id = %s", (klant_id,))

        conn.commit()
        flash("✅ Klant en gekoppelde gegevens zijn volledig verwijderd.")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Fout bij verwijderen klant: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("klant_bp.klanten"))

