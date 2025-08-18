import mysql.connector
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import os
from dotenv import load_dotenv
load_dotenv()
import re
import logging


from DB_Config import db_config
index_bp = Blueprint("index_bp", __name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


secret_key = os.getenv("secret_key")
ADMIN_GEBRUIKER = os.getenv("ADMIN_GEBRUIKER")
ADMIN_WACHTWOORD = os.getenv("ADMIN_WACHTWOORD")

log = logging.getLogger("security")

# Database-configuratie uit .env

def get_db_connection():
    return mysql.connector.connect(**db_config)


@index_bp.route("/")
def index():
    if "gebruiker" not in session:
        return redirect(url_for("index_bp.login"))
    return render_template("index.html")

@index_bp.route("/login", methods=["GET", "POST"])
def login():
    foutmelding = None

    if request.method == "POST":
        gebruikersnaam = (request.form.get("gebruikersnaam") or "").strip()
        wachtwoord     = request.form.get("wachtwoord") or ""

        # Hardcoded admin (als je dit houdt, zet dit ZEKER alleen in .env op de server)
        if gebruikersnaam == ADMIN_GEBRUIKER and wachtwoord == ADMIN_WACHTWOORD:
            session.clear()
            session["gebruiker"] = ADMIN_GEBRUIKER
            session["rol"] = "admin"
            return redirect(url_for("index_bp.index"))

        # 1) Server-side input checks (voorkomt rare payloads en scheelt ruis)
        if not USERNAME_RE.match(gebruikersnaam) or len(wachtwoord) > 128:
            # zelfde foutmelding als bij mislukte login, geen hints
            return render_template("login.html", foutmelding="❌ Onjuiste gebruikersnaam of wachtwoord."), 401

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            # Optioneel: prepared=True kan server-side prepares forceren
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, gebruikersnaam, wachtwoord_hash, rol "
                "FROM gebruikers WHERE gebruikersnaam = %s",
                (gebruikersnaam,)
            )
            gebruiker = cur.fetchone()

            ok = False
            if gebruiker:
                # bcrypt-check; stored hash als TEXT/VARCHAR
                ok = bcrypt.checkpw(
                    wachtwoord.encode("utf-8"),
                    gebruiker["wachtwoord_hash"].encode("utf-8")
                )

            if not ok:
                # geen user-enumeration of SQL-errors naar buiten
                return render_template("login.html", foutmelding="❌ Onjuiste gebruikersnaam of wachtwoord."), 401

            session.clear()
            session["gebruiker"] = gebruiker["gebruikersnaam"]
            session["rol"] = gebruiker["rol"]
            return redirect(url_for("index_bp.index"))

        except Exception as e:
            # Log intern, maar toon niets specifieks aan de gebruiker
            log.warning("Login error for '%s': %s", gebruikersnaam, e)
            return render_template("login.html", foutmelding="❌ Onjuiste gebruikersnaam of wachtwoord."), 401
        finally:
            try:
                if cur: cur.close()
            finally:
                if conn: conn.close()

    return render_template("login.html", foutmelding=foutmelding)
@index_bp.route("/logout")
def logout():
    session.pop("gebruiker", None)
    session.pop("rol", None)
    return redirect(url_for("index_bp.login"))

@index_bp.route("/registreren")
def registreren():
    return "<h2>Registratiepagina komt nog!</h2><p><a href='/login'>← Terug naar login</a></p>"

print("Verbonden met database:", db_config["database"])