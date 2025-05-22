from flask import Blueprint, Response
import sqlite3
import csv
import io

klant_download_bp = Blueprint('klant_download_bp', __name__)


@klant_download_bp.route('/klanten/download')

def download_klanten_csv():
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam, emailadres, telefoon, adres FROM klanten")
    klanten = cursor.fetchall()
    conn.close()

    # CSV genereren in geheugen
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Naam', 'Emailadres', 'Telefoon', 'Adres'])  # Header
    writer.writerows(klanten)

    # Response instellen met download headers
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=klanten.csv"
    return response

# exporteer de blueprint correct
__all__ = ['klant_download_bp']
