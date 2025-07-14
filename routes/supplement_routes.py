import mysql.connector
from flask import render_template, Blueprint, current_app
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
