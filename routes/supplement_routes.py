import mysql.connector
from flask import render_template, Blueprint, current_app,flash, redirect, url_for, session, request
from dotenv import load_dotenv
import os

# Laad .env variabelen
load_dotenv()

# Blueprint aanmaken voor supplementroutes
supplement_bp = Blueprint("supplement_bp", __name__, url_prefix="/supplementen")

# Databaseconfiguratie
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# Route: overzicht van alle supplementen
@supplement_bp.route("/")
def toon_supplementen():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, naam, andere_namen, lost_op_in, eigenschap_functie, 
               bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden, 
               bouwstof, eigenschappen 
        FROM supplementen
        """
    )

    supplementen = cursor.fetchall()

    kolommen = [
        "id",
        "naam",
        "andere_namen",
        "lost_op_in",
        "eigenschap_functie",
        "bij_tekort",
        "inzetten_bij",
        "voedingsbronnen",
        "bijzonderheden",
        "bouwstof",
        "eigenschappen",
    ]

    supplementen_dicts = [dict(zip(kolommen, row)) for row in supplementen]

    cursor.close()
    conn.close()

    return render_template("supplementen.html", supplementen=supplementen_dicts)


# Route: detailpagina van één supplement
@supplement_bp.route("/<int:id>")
def detail_supplement(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT naam, andere_namen, lost_op_in, eigenschap_functie, bij_tekort, 
               inzetten_bij, voedingsbronnen, bijzonderheden, bouwstof, eigenschappen 
        FROM supplementen 
        WHERE id = %s
        """,
        (id,),
    )

    row = cursor.fetchone()

    kolommen = [
        "naam",
        "andere_namen",
        "lost_op_in",
        "eigenschap_functie",
        "bij_tekort",
        "inzetten_bij",
        "voedingsbronnen",
        "bijzonderheden",
        "bouwstof",
        "eigenschappen",
    ]

    supplement = dict(zip(kolommen, row)) if row else None

    cursor.close()
    conn.close()

    if supplement:
        return render_template("supplement_detail.html", supplement=supplement)
    else:
        return "Supplement niet gevonden", 404

@supplement_bp.route("/supplement/<supplement_naam>/verwijderen", methods=["POST"])
def supplement_verwijderen(supplement_naam):
    print("Verwijderverzoek ontvangen voor:", supplement_naam)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(buffered=True)


    try:
        # Zoek het ID van het supplement
        cursor.execute("SELECT id FROM supplementen WHERE naam = %s", (supplement_naam,))
        result = cursor.fetchone()
        print("Zoekresultaat:", result)

        if result:
            supplement_id = result[0]

            # Verwijder het supplement
            cursor.execute("DELETE FROM supplementen WHERE id = %s", (supplement_id,))
            conn.commit()
            print(f"Supplement '{supplement_naam}' met ID {supplement_id} verwijderd.")
            flash(f"Supplement '{supplement_naam}' is verwijderd.")
        else:
            print(f"Supplement '{supplement_naam}' niet gevonden in de database.")
            flash(f"Supplement '{supplement_naam}' niet gevonden.")

    except Exception as e:
        conn.rollback()
        print("Fout tijdens verwijderen:", e)
        flash(f"Verwijderen mislukt: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("supplement_bp.toon_supplementen"))



# In supplement_routes.py of je blueprintbestand
@supplement_bp.route("/toevoegen", methods=["GET", "POST"])

def supplement_toevoegen():
    print("Formulier is verzonden!")

    if request.method == "POST":
        print("Naam:", request.form.get("naam"))
        print("Andere Namen:", request.form.get("andere_namen"))
        print("Lost Op In:", request.form.get("lost_op_in"))
        print("Functie:", request.form.get("functie"))
        print("Bij Tekort:", request.form.get("bij_tekort"))
        print("Inzetten Bij:", request.form.get("inzetten_bij"))
        print("Voedingsbronnen:", request.form.get("voedingsbronnen"))
        print("Bijzonderheden:", request.form.get("bijzonderheden"))
        print("Bouwstof:", request.form.get("bouwstof"))
        print("Eigenschappen:", request.form.get("eigenschappen"))

        naam = request.form.get("naam")
        andere_namen = request.form.get("andere_namen")
        lost_op_in = request.form.get("lost_op_in")
        functie = request.form.get("functie")
        bij_tekort = request.form.get("bij_tekort")
        inzetten_bij = request.form.get("inzetten_bij")
        voedingsbronnen = request.form.get("voedingsbronnen")
        bijzonderheden = request.form.get("bijzonderheden")
        bouwstof = request.form.get("bouwstof")
        eigenschappen = request.form.get("eigenschappen")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO supplementen 
                (naam, andere_namen, lost_op_in, eigenschap_functie, bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden, bouwstof, eigenschappen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                naam, andere_namen, lost_op_in, functie, bij_tekort,
                inzetten_bij, voedingsbronnen, bijzonderheden, bouwstof, eigenschappen
            ))

            conn.commit()
            print(" Supplement toegevoegd:", naam)
            flash(f" Supplement '{naam}' toegevoegd.")
            return redirect(url_for("supplement_bp.toon_supplementen"))

        except Exception as e:
            conn.rollback()
            print(" Fout bij toevoegen:", e)  # <- DIT is wat je nodig hebt
            flash(f" Fout bij toevoegen: {e}")

        finally:
            cursor.close()
            conn.close()

    return render_template("supplement_toevoegen.html")

