import sqlite3
from flask import render_template, url_for, request, redirect, flash, Blueprint

supplement_bp = Blueprint('supplement_bp', __name__, url_prefix='/supplementen')

@supplement_bp.route('/')
def toon_supplementen():
    # Verbinden met database
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()

    # Data ophalen (nu inclusief id)
    cursor.execute('SELECT id, naam, andere_namen, lost_op_in, eigenschap_functie, bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden, bouwstof, eigenschappen FROM supplementen')

    supplementen = cursor.fetchall()

    # Kolomnamen koppelen aan de waardes (ook id toevoegen)
    kolommen = ['id', 'naam', 'andere_namen', 'lost_op_in', 'eigenschap_functie',
                'bij_tekort', 'inzetten_bij', 'voedingsbronnen', 'bijzonderheden',
                'bouwstof', 'eigenschappen']

    supplementen_dicts = [dict(zip(kolommen, row)) for row in supplementen]

    conn.close()

    return render_template('supplementen.html', supplementen=supplementen_dicts)


@supplement_bp.route('/<int:id>')
def detail_supplement(id):
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()

    cursor.execute('SELECT naam, andere_namen, lost_op_in, eigenschap_functie, bij_tekort, inzetten_bij, voedingsbronnen, bijzonderheden, bouwstof, eigenschappen FROM supplementen WHERE id = ?', (id,))

    row = cursor.fetchone()

    kolommen = ['naam', 'andere_namen', 'lost_op_in', 'eigenschap_functie',
                'bij_tekort', 'inzetten_bij', 'voedingsbronnen', 'bijzonderheden',
                'bouwstof', 'eigenschappen']

    supplement = dict(zip(kolommen, row)) if row else None

    conn.close()

    if supplement:
        return render_template('supplement_detail.html', supplement=supplement)
    else:
        return "Supplement niet gevonden", 404
