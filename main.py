# Importeer benodigde modules van Flask
from flask import Flask

# Importeer de verschillende route-bestanden (Blueprints)
from routes.index_routes import index_bp
from routes.plant_routes import plant_bp
from routes.klacht_routes import klacht_bp
from routes.klant_routes import klant_bp
from routes.supplement_routes import supplement_bp
from routes.klant_download_routes import klant_download_bp

# Maak een nieuwe Flask-applicatie aan
app = Flask(__name__)
# Stel de geheime sleutel in voor sessiebeheer
app.secret_key = "geheim123"

# Map waarin geüploade bestanden opgeslagen worden
UPLOAD_FOLDER = "static/uploads"
# Sta alleen bepaalde bestandstypen toe om te uploaden
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
# Voeg de uploadmap toe aan de configuratie van Flask
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Zet admin gebruikersnaam en wachtwoord voor eenvoudige login/authenticatie
ADMIN_GEBRUIKER = "admin"
ADMIN_WACHTWOORD = "test123"

# Registreer alle route-blueprints bij de Flask-app
app.register_blueprint(index_bp)
app.register_blueprint(plant_bp)
app.register_blueprint(klacht_bp)
app.register_blueprint(klant_bp)
app.register_blueprint(supplement_bp)
app.register_blueprint(klant_download_bp)

# Importeer modules voor threading en automatisch openen van de browser
import threading
import webbrowser


# Definieer een functie die automatisch de standaardbrowser opent op het juiste adres
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


# Start de server als dit bestand direct wordt uitgevoerd
if __name__ == "__main__":
    # Start een timer die na 1.25 seconden de browser opent
    threading.Timer(1.25, open_browser).start()
    # Start de Flask webserver op poort 5000
    app.run()
