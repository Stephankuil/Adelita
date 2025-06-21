import sys
import os

# Voeg het bovenliggende pad toe aan sys.path zodat modules in andere mappen gevonden worden
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import Flask
from unittest.mock import patch, MagicMock

# Importeer Flask Blueprints
from routes.index_routes import index_bp
from routes.plant_routes import plant_bp
from routes.klant_routes import klant_bp
from routes.klacht_routes import klacht_bp


# Setup van de Flask app met blueprints
@pytest.fixture
def app():
    template_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "templates")
    )
    app = Flask(__name__, template_folder=template_path)
    app.secret_key = "testsecret"
    app.register_blueprint(index_bp)
    app.register_blueprint(klacht_bp)
    app.register_blueprint(plant_bp)
    app.register_blueprint(klant_bp)
    app.config["DEBUG"] = True
    return app


# Maak een testclient op basis van de Flask app
@pytest.fixture
def client(app):
    return app.test_client()


# ---- AUTHENTICATIE EN LOGIN ----


# Test dat niet-ingelogde gebruiker wordt doorgestuurd naar de loginpagina
def test_index_redirects_when_not_logged_in(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


# Test dat de loginpagina bereikbaar is via GET
def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"login" in response.data.lower()


# Test succesvolle login met correcte inloggegevens
def test_login_post_correct(client):
    response = client.post(
        "/login",
        data={"gebruikersnaam": "admin", "wachtwoord": "test123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"index" in response.data.lower() or b"<html" in response.data.lower()


# Test mislukte login met foute gegevens
def test_login_post_incorrect(client):
    response = client.post(
        "/login", data={"gebruikersnaam": "fout", "wachtwoord": "fout"}
    )
    assert response.status_code == 200
    assert b"onjuiste gebruikersnaam" in response.data.lower()


# Test of registratiepagina goed laadt
def test_registreren_route(client):
    response = client.get("/registreren")
    assert response.status_code == 200
    assert b"Registratiepagina" in response.data


# Test of logout de gebruiker terugstuurt naar de loginpagina
def test_logout_redirects_to_login(client):
    with client.session_transaction() as sess:
        sess["gebruiker"] = "admin"
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


# Test toegang tot indexpagina als je bent ingelogd
def test_index_access_when_logged_in(client):
    with client.session_transaction() as sess:
        sess["gebruiker"] = "admin"
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data or b"index" in response.data


# ---- ROUTES MET DATABASE: MOCKING ----


# Test dat klachtenlijst geladen wordt met mocked database
@patch("routes.klacht_routes.sqlite3.connect")
def test_klachten_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, "Hoofdpijn", "Pijn in het hoofd")]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klachten")
    assert response.status_code == 200
    assert b"<html" in response.data or b"klachten" in response.data.lower()


# Test detailpagina van een bestaande klacht
@patch("routes.klacht_routes.sqlite3.connect")
def test_klacht_detail_route_bestaande_klacht(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Beschrijving van hoofdpijn")
    mock_cursor.fetchall.side_effect = [
        [("PlantA",)],  # gekoppelde_planten
        [(1, "PlantA")],  # alle_planten
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klacht/Hoofdpijn")
    assert response.status_code == 200
    assert b"<html" in response.data or b"hoofdpijn" in response.data.lower()


# Test voor niet-bestaande klacht
@patch("routes.klacht_routes.sqlite3.connect")
def test_klacht_detail_route_niet_bestaande_klacht(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klacht/GeenbestaandeKlacht")
    assert response.status_code == 200
    assert b"niet gevonden" in response.data.lower()


# Test voor laden van klantenoverzicht
@patch("routes.klant_routes.sqlite3.connect")
def test_klanten_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, "Testklant")]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klanten")
    assert response.status_code == 200
    assert b"<html" in response.data or b"klanten" in response.data.lower()


# Test detailweergave van klantgegevens
@patch("routes.klant_routes.sqlite3.connect")
def test_klant_detail_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Testklant", "email", "telefoon", "adres")
    mock_cursor.fetchall.side_effect = [[], [], [], [], []]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klant/1")
    assert response.status_code == 200
    assert b"<html" in response.data or b"klant" in response.data.lower()


# Test pagina met behandelingen per klant
@patch("routes.klant_routes.sqlite3.connect")
def test_klanten_behandelingen_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [
        [(1, "Testklant")],
        [(1, "Behandeling1", "2025-01-01")],
        [("Hoofdpijn",)],
        [("PlantA",)],
    ]
    mock_cursor.fetchone.side_effect = [(1, "Behandeling1", "2025-01-01")]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klanten/behandelingen")
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()


# Test POST-verzoek voor het aanmaken van een nieuwe klant
@patch("routes.klant_routes.sqlite3.connect")
def test_nieuwe_klant_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/nieuwe_klant",
        data={
            "naam": "Testklant",
            "emailadres": "test@example.com",
            "telefoon": "0612345678",
            "adres": "Straat 1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"klant" in response.data.lower()


# Test POST-verzoek om een notitie toe te voegen
@patch("routes.klant_routes.sqlite3.connect")
def test_notitie_toevoegen_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/notitie_toevoegen",
        data={"inhoud": "Testnotitie"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"notitie" in response.data.lower()


# Test POST-verzoek om een behandeling toe te voegen aan een klant
@patch("routes.klant_routes.sqlite3.connect")
def test_nieuwe_behandeling_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/nieuwe_behandeling",
        data={
            "naam": "Testbehandeling",
            "datum": "2025-01-01",
            "klachten": ["1"],
            "planten": ["1"],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()


# Test POST voor behandeling koppeling
@patch("routes.klant_routes.sqlite3.connect")
def test_behandeling_toevoegen_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/behandeling_toevoegen",
        data={"behandeling": "Testbehandeling"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()


# Test POST om behandeling te updaten
@patch("routes.klant_routes.sqlite3.connect")
def test_update_behandeling_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/update_behandeling",
        data={"behandeling": "Update"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()


# Test POST om afspraak toe te voegen
@patch("routes.klant_routes.sqlite3.connect")
def test_nieuwe_afspraak_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/nieuwe_afspraak/1",
        data={
            "datum": "2025-05-01",
            "tijd": "10:00",
            "onderwerp": "Testafspraak",
            "locatie": "Praktijk",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"afspraak" in response.data.lower()


# Test ophalen van plantenlijst
@patch("routes.plant_routes.sqlite3.connect")
def test_planten_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("PlantA",)]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/planten")
    assert response.status_code == 200
    assert b"<html" in response.data or b"plant" in response.data.lower()


# Test weergave van plantinformatie
@patch("routes.plant_routes.sqlite3.connect")
def test_plant_info_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        ("PlantA", "Beschrijving", "Botanische naam", "bla", "bla", "bla", "bla", None),
        (1,),
    ]
    mock_cursor.description = [
        ("naam",),
        ("beschrijving",),
        ("botanische_naam",),
        ("col4",),
        ("col5",),
        ("col6",),
        ("col7",),
        ("col8",),
    ]
    mock_cursor.fetchall.return_value = [("Hoofdpijn",)]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/plant/PlantA/info")
    assert response.status_code == 200
    assert b"<html" in response.data or b"plant" in response.data.lower()


# Test detailpagina van een plant
@patch("routes.plant_routes.sqlite3.connect")
def test_plant_detail_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (1,),  # plant_id
        ("PlantA", "Beschrijving", "Botanische naam", "bla", "bla", "bla", "bla", None),
    ]
    mock_cursor.description = [
        ("naam",),
        ("beschrijving",),
        ("botanische_naam",),
        ("col4",),
        ("col5",),
        ("col6",),
        ("col7",),
        ("col8",),
    ]
    mock_cursor.fetchall.side_effect = [[(1, "Hoofdpijn")], [(1,)]]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/plant/PlantA")
    assert response.status_code == 200
    assert b"<html" in response.data or b"plant" in response.data.lower()


# Test POST-verzoek voor koppelen plant aan klacht
@patch("routes.plant_routes.sqlite3.connect")
def test_koppel_plant_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [None, ("Hoofdpijn",), (1, "Beschrijving")]
    mock_cursor.fetchall.side_effect = [[("PlantA",)], [(1, "PlantA")]]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/koppel_plant", data={"klacht_id": "1", "plant_id": "1"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"klacht" in response.data.lower()


# Test POST-verzoek voor verwijderen van plant-klacht-koppeling
@patch("routes.plant_routes.sqlite3.connect")
def test_verwijder_plant_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [(1,), ("Hoofdpijn",), (1, "Beschrijving")]
    mock_cursor.fetchall.side_effect = [[("PlantA",)], [(1, "PlantA")]]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/verwijder_plant",
        data={"plant_naam": "PlantA", "klacht_id": "1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"klacht" in response.data.lower()
