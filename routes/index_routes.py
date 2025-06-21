# Importeer benodigde modules van Flask
from flask import Blueprint, render_template, request, redirect, url_for, session

# Maak een Blueprint aan voor de index-routes
index_bp = Blueprint("index_bp", __name__)

# Simpele hardcoded admin-inloggegevens
ADMIN_GEBRUIKER = "admin"
ADMIN_WACHTWOORD = "test123"


# Route voor de startpagina ("/")
@index_bp.route("/")
def index():
    # Als de gebruiker niet is ingelogd, stuur door naar de loginpagina
    if "gebruiker" not in session:
        return redirect(url_for("index_bp.login"))

    # Als de gebruiker is ingelogd, toon de index.html pagina
    return render_template("index.html")


# Route voor inloggen ("/login"), ondersteunt GET en POST
@index_bp.route("/login", methods=["GET", "POST"])
def login():
    foutmelding = None  # Variabele om foutmeldingen op te slaan

    # Verwerk formulier indien verstuurd via POST
    if request.method == "POST":
        gebruikersnaam = request.form["gebruikersnaam"]
        wachtwoord = request.form["wachtwoord"]

        # Controleer of gebruikersnaam en wachtwoord overeenkomen met admin
        if gebruikersnaam == ADMIN_GEBRUIKER and wachtwoord == ADMIN_WACHTWOORD:
            session["gebruiker"] = gebruikersnaam  # Sla gebruiker op in sessie
            return redirect(url_for("index_bp.index"))  # Doorsturen naar index
        else:
            foutmelding = "Onjuiste gebruikersnaam of wachtwoord."  # Foutmelding tonen

    # Toon loginpagina (GET of bij mislukte inlog)
    return render_template("login.html", foutmelding=foutmelding)


# Route voor registreren (placeholder)
@index_bp.route("/registreren")
def registreren():
    # Simpele HTML-reactie als placeholder voor de registratiepagina
    return "<h2>Registratiepagina komt nog!</h2><p><a href='/login'>← Terug naar login</a></p>"


# Route voor uitloggen
@index_bp.route("/logout")
def logout():
    session.pop("gebruiker", None)  # Verwijder gebruiker uit sessie
    return redirect(url_for("index_bp.login"))  # Redirect naar loginpagina
