from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
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

# 🔒 Veilig JSON inladen zonder crash
def safe_json_load(value, default):
    try:
        return json.loads(value) if value else default
    except json.JSONDecodeError:
        return default

# 📄 Route: overzicht van paddenstoelen
@paddenstoel_bp.route("/paddenstoelen")
def index():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nederlandse_naam FROM paddenstoelen ORDER BY nederlandse_naam")
    paddenstoelen = cursor.fetchall()
    conn.close()
    return render_template("paddenstoelen.html", paddenstoelen=paddenstoelen)

# 🔍 Route: detailpagina van één paddenstoel
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
        "andere_namen": safe_json_load(row.get("andere_namen"), []),
        "familie": row["familie"],
        "stoffen": safe_json_load(row.get("belangrijkste_werkzame_stoffen"), []),
        "toepassing": safe_json_load(row.get("toepassing"), []),
        "werking": safe_json_load(row.get("werking"), [])
    }

    return render_template("paddenstoelen_info.html", pad=detail)
@paddenstoel_bp.route("/paddenstoel/toevoegen", methods=["GET", "POST"])
def paddenstoel_toevoegen():
    if request.method == "POST":
        familie = request.form.get("familie")
        stoffen_raw = request.form.get("belangrijkste_werkzame_stoffen", "")
        toepassing_raw = request.form.get("toepassing", "")
        werking_raw = request.form.get("werking", "")

        # Alle 4 naamvelden als lijsten ophalen
        latijnse_namen = request.form.getlist("latijnse_naam[]")
        nederlandse_namen = request.form.getlist("nederlandse_naam[]")
        chinese_namen = request.form.getlist("chinese_naam[]")
        japanse_namen = request.form.getlist("japanse_naam[]")

        # Maak een lijst van dicts met ingevulde naamgroepen (lege negeren)
        naam_groepen = []
        for lat, ned, chi, jap in zip(latijnse_namen, nederlandse_namen, chinese_namen, japanse_namen):
            if lat.strip() or ned.strip() or chi.strip() or jap.strip():
                naam_groepen.append({
                    "latijnse_naam": lat.strip(),
                    "nederlandse_naam": ned.strip(),
                    "chinese_naam": chi.strip(),
                    "japanse_naam": jap.strip(),
                })

        # Sla naam_groepen op als JSON string
        namen_json = json.dumps(naam_groepen, ensure_ascii=False)

        stoffen = json.dumps([s.strip() for s in stoffen_raw.split(",") if s.strip()])
        toepassing = json.dumps([s.strip() for s in toepassing_raw.split(",") if s.strip()])
        werking = json.dumps([s.strip() for s in werking_raw.split(",") if s.strip()])

        # Kies primaire Nederlandse naam als eerste ingevulde nederlandse naam, anders leeg
        primaire_nederlandse_naam = ""
        for ng in naam_groepen:
            if ng["nederlandse_naam"]:
                primaire_nederlandse_naam = ng["nederlandse_naam"]
                break

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO paddenstoelen (
                nederlandse_naam,
                andere_namen,
                familie,
                belangrijkste_werkzame_stoffen,
                toepassing,
                werking
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (primaire_nederlandse_naam, namen_json, familie, stoffen, toepassing, werking))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Paddenstoel toegevoegd.")
        return redirect(url_for("paddenstoel_bp.index"))

    return render_template("paddenstoelen_toevoegen.html")



@paddenstoel_bp.route("/paddenstoelen/<int:paddenstoel_id>/verwijderen", methods=["POST"])
def paddenstoel_verwijderen(paddenstoel_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM paddenstoelen WHERE id = %s", (paddenstoel_id,))
        conn.commit()
        flash("🗑️ Paddenstoel verwijderd.")
    except Exception as e:
        conn.rollback()
        flash(f"❌ Fout bij verwijderen: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("paddenstoel_bp.index"))
