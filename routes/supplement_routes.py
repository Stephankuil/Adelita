import sqlite3
from flask import render_template, Blueprint

# Blueprint aanmaken voor supplementroutes, met URL-prefix /supplementen
supplement_bp = Blueprint("supplement_bp", __name__, url_prefix="/supplementen")


# Route: overzicht van alle supplementen
@supplement_bp.route("/")
def toon_supplementen():
    # Verbind met de database
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal alle kolommen van supplementen op (inclusief id)
    cursor.execute(
        """
        SELECT id, naam, andere_namen, lost_op_in, eigenschap_functie, 
               bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden, 
               bouwstof, eigenschappen 
        FROM supplementen
    """
    )

    supplementen = cursor.fetchall()

    # Kolomnamen instellen
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

    # Combineer de kolomnamen met de waarden tot een lijst van dictionaries
    supplementen_dicts = [dict(zip(kolommen, row)) for row in supplementen]

    conn.close()

    # Geef de data door aan de HTML-template
    return render_template("supplementen.html", supplementen=supplementen_dicts)


# Route: detailpagina van één supplement
@supplement_bp.route("/<int:id>")
def detail_supplement(id):
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal gegevens van supplement met specifieke ID op
    cursor.execute(
        """
        SELECT naam, andere_namen, lost_op_in, eigenschap_functie, bij_tekort, 
               inzetten_bij, voedingsbronnen, bijzonderheden, bouwstof, eigenschappen 
        FROM supplementen 
        WHERE id = ?
    """,
        (id,),
    )

    row = cursor.fetchone()

    # Kolomnamen van het supplement (zonder id)
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

    # Maak dictionary van kolommen en data, als er iets gevonden is
    supplement = dict(zip(kolommen, row)) if row else None

    conn.close()

    # Als het supplement bestaat, render de detailtemplate
    if supplement:
        return render_template("supplement_detail.html", supplement=supplement)
    else:
        # Zo niet, geef 404 terug
        return "Supplement niet gevonden", 404
