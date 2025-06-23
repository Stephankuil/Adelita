# Importeer benodigde modules van Flask
from flask import Blueprint, render_template, request, redirect, url_for, session  # Voor routes, templates, formulierverwerking en sessiebeheer

# Maak een Blueprint aan voor de index-routes
index_bp = Blueprint("index_bp", __name__)  # Blueprint voor alle routes in dit bestand

# Simpele hardcoded admin-inloggegevens
ADMIN_GEBRUIKER = "admin"  # Gebruikersnaam voor admin-login
ADMIN_WACHTWOORD = "test123"  # Wachtwoord voor admin-login

# Route voor de startpagina ("/")
@index_bp.route("/")
def index():
    if "gebruiker" not in session:  # Controleer of gebruiker is ingelogd
        return redirect(url_for("index_bp.login"))  # Zo niet, stuur door naar loginpagina
    return render_template("index.html")  # Toon indexpagina als gebruiker is ingelogd

# Route voor inloggen ("/login"), ondersteunt GET en POST
@index_bp.route("/login", methods=["GET", "POST"])
def login():
    foutmelding = None  # Variabele voor foutmelding (bijv. verkeerde login)

    if request.method == "POST":  # Als formulier is verstuurd
        gebruikersnaam = request.form["gebruikersnaam"]  # Haal gebruikersnaam uit formulier
        wachtwoord = request.form["wachtwoord"]  # Haal wachtwoord uit formulier

        if gebruikersnaam == ADMIN_GEBRUIKER and wachtwoord == ADMIN_WACHTWOORD:  # Controleer adminlogin
            session["gebruiker"] = gebruikersnaam  # Sla gebruiker op in sessie
            return redirect(url_for("index_bp.index"))  # Redirect naar homepage
        else:
            foutmelding = "Onjuiste gebruikersnaam of wachtwoord."  # Toon foutmelding

    return render_template("login.html", foutmelding=foutmelding)  # Toon loginpagina (GET of na fout)

# Route voor registreren (placeholder)
@index_bp.route("/registreren")
def registreren():
    return "<h2>Registratiepagina komt nog!</h2><p><a href='/login'>← Terug naar login</a></p>"  # Placeholder HTML

# Route voor uitloggen
@index_bp.route("/logout")
def logout():
    session.pop("gebruiker", None)  # Verwijder gebruiker uit sessie
    return redirect(url_for("index_bp.login"))  # Redirect naar loginpagina
