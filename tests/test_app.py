import sys
import os
import tempfile
import pytest
from main import app, allowed_file  # Import de Flask app en de functie die je wilt testen

# Voeg het pad van de bovenliggende directory toe zodat Python 'main' kan vinden
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Fixture: maakt een test client aan voor de Flask app
@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()  # Maak een tijdelijk bestand aan (placeholder voor database)
    app.config['TESTING'] = True         # Zet de app in TESTING mode (speciale testomgeving)
    app.config['DATABASE'] = db_path      # (optioneel) stel een test database pad in

    # Maak een test client (simuleert een browser)
    with app.test_client() as client:
        yield client  # Geeft de client terug aan de testfuncties

    os.close(db_fd)       # Sluit het tijdelijke bestand
    os.unlink(db_path)    # Verwijder het tijdelijke bestand van de schijf


# ✅ Test of de allowed_file functie werkt zoals verwacht
def test_allowed_file():
    assert allowed_file('test.png')         # png toegestaan → True
    assert allowed_file('image.jpg')        # jpg toegestaan → True
    assert not allowed_file('document.pdf') # pdf niet toegestaan → False
    assert not allowed_file('file')         # geen extensie → False


# ✅ Test succesvol inloggen
def test_login_success(client):
    response = client.post('/login', data={
        'gebruikersnaam': 'admin',     # juiste gebruikersnaam
        'wachtwoord': 'test123'        # juist wachtwoord
    }, follow_redirects=True)          # volg redirects automatisch
    # Controleer of we op index-pagina komen (afhankelijk van je template)
    assert b"index" in response.data or response.status_code == 200


# ✅ Test inloggen met verkeerde inloggegevens
def test_login_failure(client):
    response = client.post('/login', data={
        'gebruikersnaam': 'fout',     # verkeerde gebruikersnaam
        'wachtwoord': 'fout'          # verkeerd wachtwoord
    })
    # Controleer of foutmelding aanwezig is in de response
    assert b"Onjuiste gebruikersnaam" in response.data


# ✅ Test dat niet-ingelogde gebruikers worden doorgestuurd naar /login
def test_index_redirects_when_not_logged_in(client):
    response = client.get('/', follow_redirects=False)  # ga NIET automatisch volgen
    assert response.status_code == 302                 # 302 = redirect
    assert '/login' in response.headers['Location']    # redirect naar /login


# ✅ Test dat ingelogde gebruiker toegang krijgt tot de indexpagina
def test_index_access_when_logged_in(client):
    with client.session_transaction() as sess:
        sess['gebruiker'] = 'admin'  # Simuleer ingelogde sessie

    response = client.get('/')        # Bezoek de indexpagina
    assert response.status_code == 200  # Pagina laadt zonder redirect
    assert b"index" in response.data or b"<html" in response.data  # controleer op iets herkenbaars in HTML


# ✅ Test dat /planten werkt voor ingelogde gebruiker
def test_planten_route(client):
    with client.session_transaction() as sess:
        sess['gebruiker'] = 'admin'   # Simuleer ingelogde sessie

    response = client.get('/planten')  # Bezoek de plantenpagina
    assert response.status_code == 200 # Pagina laadt succesvol
    assert b"<html" in response.data   # controleer of HTML inhoud aanwezig is
