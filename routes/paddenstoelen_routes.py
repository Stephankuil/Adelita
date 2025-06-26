from flask import Blueprint, render_template, abort
import sqlite3
import json

paddenstoel_bp = Blueprint("paddenstoel_bp", __name__)

@paddenstoel_bp.route("/paddenstoelen")  # <-- correct pad
def index():
    conn = sqlite3.connect("fytotherapie.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nederlandse_naam FROM paddenstoelen")
    paddenstoelen = cursor.fetchall()
    conn.close()
    return render_template("paddenstoelen.html", paddenstoelen=paddenstoelen)

@paddenstoel_bp.route("/paddenstoelen/<int:paddenstoel_id>")
def paddenstoel_detail(paddenstoel_id):
    conn = sqlite3.connect("fytotherapie.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paddenstoelen WHERE id = ?", (paddenstoel_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        abort(404)

    detail = {
        "id": row["id"],
        "nederlandse_naam": row["nederlandse_naam"],
        "andere_namen": json.loads(row["andere_namen"] or "{}"),
        "familie": row["familie"],
        "stoffen": json.loads(row["belangrijkste_werkzame_stoffen"] or "[]"),
        "toepassing": json.loads(row["toepassing"] or "[]"),
        "werking": json.loads(row["werking"] or "[]")
    }

    return render_template("paddenstoelen_info.html", pad=detail)
