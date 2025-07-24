from flask import Flask  # Importeer de Flask klasse om een webapplicatie te maken

# Importeer de verschillende route-bestanden (Blueprints)
from routes.index_routes import index_bp  # Hoofdpagina-routes
from routes.plant_routes import plant_bp  # Routes voor plantenbeheer
from routes.klacht_routes import klacht_bp  # Routes voor klachtenbeheer
from routes.klant_routes import klant_bp  # Routes voor klantbeheer
from routes.supplement_routes import supplement_bp  # Routes voor supplementenbeheer
from routes.klant_download_routes import klant_download_bp  # Routes voor klantgegevens downloaden
from routes.paddenstoelen_routes import paddenstoel_bp


app = Flask(__name__)
app.secret_key = "ietsgeheim"

# Registreer de blueprint
app.register_blueprint(paddenstoel_bp)

app = Flask(__name__)  # Maak een nieuwe Flask-app aan
app.secret_key = "geheim123"  # Geheime sleutel instellen voor sessies

UPLOAD_FOLDER = "static/uploads"  # Map waarin geüploade bestanden worden opgeslagen
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # Toegestane bestandstypes voor upload
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  # Voeg de uploadmap toe aan de configuratie

ADMIN_GEBRUIKER = "admin"  # Gebruikersnaam voor admin-login
ADMIN_WACHTWOORD = "test123"  # Wachtwoord voor admin-login

# Registreer alle blueprints (routegroepen) bij de app


app.register_blueprint(index_bp)  # Voeg index-routes toe
app.register_blueprint(plant_bp)  # Voeg plant-routes toe
app.register_blueprint(klacht_bp)  # Voeg klacht-routes toe
app.register_blueprint(klant_bp)  # Voeg klant-routes toe
app.register_blueprint(supplement_bp)  # Voeg supplement-routes toe
app.register_blueprint(klant_download_bp)  # Voeg download-routes toe

app.register_blueprint(paddenstoel_bp)

import threading  # Voor het starten van taken op de achtergrond
import webbrowser  # Voor het openen van de standaardbrowser


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True


def open_browser():  # Definieer een functie om de browser te openen
    webbrowser.open_new("http://127.0.0.1:5000/")  # Open de standaardbrowser op het juiste adres

if __name__ == "__main__":  # Als dit script direct wordt uitgevoerd...
    threading.Timer(1.25, open_browser).start()  # Wacht 1.25 seconden en open dan de browser
    app.run()  # Start de Flask-server op poort 5000
