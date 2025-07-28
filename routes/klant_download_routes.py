from flask import Blueprint, Response
import mysql.connector
import csv
import io
from dotenv import load_dotenv
import os
from DB_Config import db_config
# 🔐 Laad .env-variabelen
load_dotenv()

# 📦 Haal MySQL-config op uit .env


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
