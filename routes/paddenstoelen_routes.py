from flask import Blueprint, render_template, abort
import mysql.connector
import json
import os
from dotenv import load_dotenv

load_dotenv()

paddenstoel_bp = Blueprint("paddenstoel_bp", __name__)

# DB-configuratie
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Route: overzicht van paddenstoelen
@paddenstoel_bp.route("/paddenstoelen")
def index():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nederlandse_naam FROM paddenstoelen ORDER BY nederlandse_naam")
    paddenstoelen = cursor.fetchall()
    conn.close()
    return render_template("paddenstoelen.html", paddenstoelen=paddenstoelen)

# Route: detailpagina van één paddenstoel
@paddenstoel_bp.route("/paddenstoelen/<int:paddenstoel_id>")
def paddenstoel_detail(paddenstoel_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM paddenstoelen WHERE id = %s", (paddenstoel_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        abort(404)

    detail = {
        "id": row["id"],
        "nederlandse_naam": row["nederlandse_naam"],
        "andere_namen": json.loads(row.get("andere_namen") or "{}"),
        "familie": row["familie"],
        "stoffen": json.loads(row.get("belangrijkste_werkzame_stoffen") or "[]"),
        "toepassing": json.loads(row.get("toepassing") or "[]"),
        "werking": json.loads(row.get("werking") or "[]")
    }

    return render_template("paddenstoelen_info.html", pad=detail)
