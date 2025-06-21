from flask import Blueprint, Response
import sqlite3
import csv
import io

# Maak een Blueprint voor het downloaden van klantgegevens
klant_download_bp = Blueprint("klant_download_bp", __name__)


# Route om de klanten als CSV-bestand te downloaden
@klant_download_bp.route("/klanten/download")
def download_klanten_csv():
    # Verbind met de SQLite-database
    conn = sqlite3.connect("fytotherapie.db")
    cursor = conn.cursor()

    # Haal alle klantgegevens op (id, naam, email, telefoon, adres)
    cursor.execute("SELECT id, naam, emailadres, telefoon, adres FROM klanten")
    klanten = cursor.fetchall()

    # Sluit de databaseverbinding
    conn.close()

    # Maak een in-memory CSV-bestand
    output = io.StringIO()
    writer = csv.writer(output)

    # Schrijf de kolomnamen (header)
    writer.writerow(["ID", "Naam", "Emailadres", "Telefoon", "Adres"])

    # Schrijf alle klantgegevens als rijen
    writer.writerows(klanten)

    # Stel de HTTP-response in als CSV-bestand met download header
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=klanten.csv"

    # Geef het bestand terug aan de gebruiker
    return response


# Zorg dat deze blueprint geëxporteerd kan worden bij import *
__all__ = ["klant_download_bp"]
