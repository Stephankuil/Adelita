from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename
import webbrowser

from flask import g
import sqlite3

from routes.index_routes import index_bp
from routes.plant_routes import plant_bp
from routes.klacht_routes import klacht_bp
from routes.klant_routes import klant_bp
from routes.supplement_routes import supplement_bp
from routes.klant_download_routes import klant_download_bp

app = Flask(__name__)
app.secret_key = 'geheim123'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# bovenin je app.py
ADMIN_GEBRUIKER = "admin"
ADMIN_WACHTWOORD = "test123"







app.register_blueprint(index_bp)
app.register_blueprint(plant_bp)
app.register_blueprint(klacht_bp)

app.register_blueprint(klant_bp)
app.register_blueprint(supplement_bp)
app.register_blueprint(klant_download_bp)


# Alle planten

# Alle klachten


# Koppel plant aan klacht




import threading
import webbrowser

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run()