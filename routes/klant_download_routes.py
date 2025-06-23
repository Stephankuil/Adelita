from flask import Blueprint, Response  # Importeer Blueprint voor routing en Response voor HTTP-antwoorden
import sqlite3  # Voor verbinding met de SQLite-database
import csv  # Voor het genereren van CSV-bestanden
import io  # Voor in-memory bestandsobjecten

# Maak een Blueprint voor het downloaden van klantgegevens
klant_download_bp = Blueprint("klant_download_bp", __name__)  # Blueprint genaamd 'klant_download_bp'

# Route om de klanten als CSV-bestand te downloaden
@klant_download_bp.route("/klanten/download")
def download_klanten_csv():
    conn = sqlite3.connect("fytotherapie.db")  # Verbind met de database
    cursor = conn.cursor()  # Maak een cursor aan

    cursor.execute("SELECT id, naam, emailadres, telefoon, adres FROM klanten")  # Haal alle klantgegevens op
    klanten = cursor.fetchall()  # Sla alle opgehaalde rijen op in een lijst

    conn.close()  # Sluit de verbinding met de database

    output = io.StringIO()  # Maak een tijdelijk tekstbestand in het geheugen
    writer = csv.writer(output)  # Maak een CSV-writer

    writer.writerow(["ID", "Naam", "Emailadres", "Telefoon", "Adres"])  # Schrijf de kolomnamen als header
    writer.writerows(klanten)  # Schrijf alle klantgegevens naar het CSV-bestand

    response = Response(output.getvalue(), mimetype="text/csv")  # Zet de inhoud om naar een HTTP-response als CSV
    response.headers["Content-Disposition"] = "attachment; filename=klanten.csv"  # Geef het bestand een downloadnaam

    return response  # Stuur het CSV-bestand terug als download

# Zorg dat deze blueprint geëxporteerd kan worden bij import *
__all__ = ["klant_download_bp"]  # Alleen deze naam wordt geëxporteerd bij from ... import *
