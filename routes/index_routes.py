import mysql.connector
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import os
from dotenv import load_dotenv
load_dotenv()

index_bp = Blueprint("index_bp", __name__)




secret_key = os.getenv("secret_key")
ADMIN_GEBRUIKER = os.getenv("ADMIN_GEBRUIKER")
ADMIN_WACHTWOORD = os.getenv("ADMIN_WACHTWOORD")



# Database-configuratie uit .env
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}



@index_bp.route("/")
def index():
    if "gebruiker" not in session:
        return redirect(url_for("index_bp.login"))
    return render_template("index.html")

@index_bp.route("/login", methods=["GET", "POST"])
def login():
    foutmelding = None

    if request.method == "POST":
        gebruikersnaam = request.form["gebruikersnaam"]
        wachtwoord = request.form["wachtwoord"]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = %s", (gebruikersnaam,))
        gebruiker = cursor.fetchone()
        conn.close()

        if gebruiker and bcrypt.checkpw(wachtwoord.encode("utf-8"), gebruiker["wachtwoord_hash"].encode("utf-8")):
            session["gebruiker"] = gebruiker["gebruikersnaam"]
            session["rol"] = gebruiker["rol"]
            return redirect(url_for("index_bp.index"))
        else:
            foutmelding = "❌ Onjuiste gebruikersnaam of wachtwoord."

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