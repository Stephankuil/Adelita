from flask import Blueprint, Response
import mysql.connector
import csv
import io
from dotenv import load_dotenv
import os

# 🔐 Laad .env-variabelen
load_dotenv()

# 📦 Haal MySQL-config op uit .env
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# 📥 Blueprint aanmaken
klant_download_bp = Blueprint("klant_download_bp", __name__)


@klant_download_bp.route("/klanten/download")
def download_klanten_csv():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("SELECT id, naam, emailadres, telefoon, adres FROM klanten")
    klanten = cursor.fetchall()

    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Naam", "Emailadres", "Telefoon", "Adres"])
    writer.writerows(klanten)

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=klanten.csv"

    return response


# Optioneel voor import *
__all__ = ["klant_download_bp"]
