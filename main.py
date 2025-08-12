from flask import Flask, request, redirect  # Importeer de Flask klasse om een webapplicatie te maken
import os
from flask_wtf.csrf import CSRFProtect, CSRFError
# Importeer de verschillende route-bestanden (Blueprints)
from routes.index_routes import index_bp  # Hoofdpagina-routes
from routes.plant_routes import plant_bp  # Routes voor plantenbeheer
from routes.klacht_routes import klacht_bp  # Routes voor klachtenbeheer
from routes.klant_routes import klant_bp  # Routes voor klantbeheer
from routes.supplement_routes import supplement_bp  # Routes voor supplementenbeheer
from routes.klant_download_routes import klant_download_bp  # Routes voor klantgegevens downloaden
from routes.paddenstoelen_routes import paddenstoel_bp




app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-long-random")
app.config["WTF_CSRF_TIME_LIMIT"] = None  # optioneel
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,      # laat True in productie achter HTTPS
    REMEMBER_COOKIE_SECURE=True,
)

# CSRF
csrf = CSRFProtect(app)

# (optioneel) nette CSRF-fout
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return ("CSRF validation failed", 400)

# (optioneel) forceer HTTPS in productie achter NPM
@app.before_request
def force_https():
    if os.getenv("FORCE_HTTPS", "1") == "1":
        if request.headers.get("X-Forwarded-Proto", "http") != "https":
            return redirect(request.url.replace("http://", "https://", 1), code=301)

# Security headers
@app.after_request
def set_security_headers(response):
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; font-src 'self' data:"
    )
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")   # of "DENY"
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    if os.getenv("FLASK_ENV") == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
    return response

UPLOAD_FOLDER = "static/uploads"  # Map waarin geüploade bestanden worden opgeslagen
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # Toegestane bestandstypes voor upload
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  # Voeg de uploadmap toe aan de configuratie


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




