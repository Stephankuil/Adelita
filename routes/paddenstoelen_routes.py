from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
import mysql.connector
import json
import os
from dotenv import load_dotenv
from DB_Config import db_config
load_dotenv()

paddenstoel_bp = Blueprint("paddenstoel_bp", __name__)



# 🔒 Veilig JSON inladen zonder crash
def safe_json_load(value, default):
    try:
        return json.loads(value) if value else default
    except json.JSONDecodeError:
        return default

# 📄 Route: overzicht van paddenstoelen
@paddenstoel_bp.route("/paddenstoelen")
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nederlandse_naam FROM paddenstoelen ORDER BY nederlandse_naam")
    paddenstoelen = cursor.fetchall()
    conn.close()
    return render_template("paddenstoelen.html", paddenstoelen=paddenstoelen)

@paddenstoel_bp.route("/paddenstoelen/<int:paddenstoel_id>")
def paddenstoel_detail(paddenstoel_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM paddenstoelen WHERE id = %s", (paddenstoel_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        abort(404)

    detail = {
        "id": row["id"],
        "nederlandse_naam": row["nederlandse_naam"],
        "latijnse_naam": row["latijnse_naam"],
        "japanse_naam": row["japanse_naam"],
        "chinese_naam": row["chinese_naam"],
        "familie": row["familie"],
        "stoffen": safe_json_load(row.get("belangrijkste_werkzame_stoffen"), []),
        "toepassing": safe_json_load(row.get("toepassing"), []),
        "werking": safe_json_load(row.get("werking"), [])
    }

    return render_template("paddenstoelen_info.html", pad=detail)

@paddenstoel_bp.route('/paddenstoel/toevoegen', methods=['GET', 'POST'])
def paddenstoel_toevoegen():
    if request.method == 'POST':
        latijnse_naam = request.form.get('latijnse_naam')
        nederlandse_naam = request.form.get('nederlandse_naam')
        chinese_naam = request.form.get('chinese_naam')
        japanse_naam = request.form.get('japanse_naam')
        familie = request.form.get('familie')
        stoffen_raw = request.form.get('belangrijkste_werkzame_stoffen', '')
        toepassing_raw = request.form.get('toepassing', '')
        werking_raw = request.form.get('werking', '')

        stoffen = [s.strip() for s in stoffen_raw.splitlines() if s.strip()]
        toepassing = [s.strip() for s in toepassing_raw.splitlines() if s.strip()]
        werking = [s.strip() for s in werking_raw.splitlines() if s.strip()]

        # Opslaan in database, bijv. stoffen, toepassing, werking als JSON strings
        stoffen_json = json.dumps(stoffen, ensure_ascii=False)
        toepassing_json = json.dumps(toepassing, ensure_ascii=False)
        werking_json = json.dumps(werking, ensure_ascii=False)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO paddenstoelen
            (latijnse_naam, nederlandse_naam, chinese_naam, japanse_naam, familie, belangrijkste_werkzame_stoffen, toepassing, werking)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (latijnse_naam, nederlandse_naam, chinese_naam, japanse_naam, familie, stoffen_json, toepassing_json, werking_json))

        conn.commit()
        cursor.close()
        conn.close()

        flash('✅ Paddenstoel toegevoegd.')
        return redirect(url_for('paddenstoel_bp.index'))

    return render_template('paddenstoelen_toevoegen.html')



@paddenstoel_bp.route("/paddenstoelen/<int:paddenstoel_id>/verwijderen", methods=["POST"])
def paddenstoel_verwijderen(paddenstoel_id):
    conn = mysql.connector.connect(**db_config)
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
