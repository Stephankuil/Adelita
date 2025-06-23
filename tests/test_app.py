import sys
import os

# Voeg het bovenliggende pad toe aan sys.path zodat modules in andere mappen gevonden worden
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest  # Testframework voor Python
from flask import Flask  # Flask framework
from unittest.mock import patch, MagicMock  # Voor het mocken van functies tijdens tests

# Importeer Flask Blueprints
from routes.index_routes import index_bp  # Blueprint voor login en homepage
from routes.plant_routes import plant_bp  # Blueprint voor planten
from routes.klant_routes import klant_bp  # Blueprint voor klanten
from routes.klacht_routes import klacht_bp  # Blueprint voor klachten

# Setup van de Flask app met blueprints
@pytest.fixture
def app():
    template_path = os.path.abspath(  # Pad naar templates instellen
        os.path.join(os.path.dirname(__file__), "..", "templates")
    )
    app = Flask(__name__, template_folder=template_path)  # Maak een Flask app aan met templatefolder
    app.secret_key = "testsecret"  # Zet een geheime sleutel voor sessies
    app.register_blueprint(index_bp)  # Registreer index (login) routes
    app.register_blueprint(klacht_bp)  # Registreer klacht routes
    app.register_blueprint(plant_bp)  # Registreer plant routes
    app.register_blueprint(klant_bp)  # Registreer klant routes
    app.config["DEBUG"] = True  # Zet debugmodus aan
    return app  # Geef de app terug

# Maak een testclient op basis van de Flask app
@pytest.fixture
def client(app):
    return app.test_client()  # Retourneer een client waarmee je HTTP-verzoeken kunt simuleren

# ---- AUTHENTICATIE EN LOGIN ----

# Test dat een niet-ingelogde gebruiker wordt doorgestuurd naar de loginpagina
def test_index_redirects_when_not_logged_in(client):
    response = client.get("/", follow_redirects=False)  # Vraag de rootpagina op (zonder redirects volgen)
    assert response.status_code == 302  # Verwacht een redirect (302)
    assert "/login" in response.headers["Location"]  # Controleer of redirect naar loginpagina gaat

# Test dat de loginpagina bereikbaar is via een GET-verzoek
def test_login_get(client):
    response = client.get("/login")  # Vraag de loginpagina op via GET
    assert response.status_code == 200  # Controleer of pagina geladen wordt
    assert b"login" in response.data.lower()  # Controleer of het woord 'login' in de HTML zit


# Test succesvolle login met correcte inloggegevens
# Test een correcte login met juiste gebruikersnaam en wachtwoord
def test_login_post_correct(client):
    response = client.post(  # Simuleer een POST-verzoek naar /login
        "/login",
        data={"gebruikersnaam": "admin", "wachtwoord": "test123"},  # Formulierdata met juiste inloggegevens
        follow_redirects=True,  # Volg redirect naar index
    )
    assert response.status_code == 200  # De response moet succesvol zijn
    assert b"index" in response.data.lower() or b"<html" in response.data.lower()  # Controleer of indexpagina zichtbaar is

# Test een mislukte login met verkeerde inloggegevens
def test_login_post_incorrect(client):
    response = client.post(  # Simuleer POST met foute gebruikersnaam en wachtwoord
        "/login", data={"gebruikersnaam": "fout", "wachtwoord": "fout"}
    )
    assert response.status_code == 200  # Pagina moet wel geladen worden
    assert b"onjuiste gebruikersnaam" in response.data.lower()  # Foutmelding moet zichtbaar zijn

# Test of de registratiepagina correct laadt
def test_registreren_route(client):
    response = client.get("/registreren")  # Simuleer een GET-verzoek naar de registratieroute
    assert response.status_code == 200  # De pagina moet bestaan
    assert b"Registratiepagina" in response.data  # Controleer of tekst 'Registratiepagina' op de pagina staat

# Test of de logout werkt en een redirect naar de loginpagina uitvoert
def test_logout_redirects_to_login(client):
    with client.session_transaction() as sess:  # Open een sessie om de gebruiker handmatig in te stellen
        sess["gebruiker"] = "admin"  # Stel gebruiker in alsof die is ingelogd
    response = client.get("/logout")  # Roep de logout route aan
    assert response.status_code == 302  # Verwacht een redirect
    assert "/login" in response.headers["Location"]  # Redirect moet naar /login gaan


# Test toegang tot indexpagina als je bent ingelogd
# Test dat de indexpagina toegankelijk is als een gebruiker is ingelogd
def test_index_access_when_logged_in(client):
    with client.session_transaction() as sess:  # Open een sessie
        sess["gebruiker"] = "admin"  # Simuleer dat de gebruiker is ingelogd
    response = client.get("/")  # Vraag de rootpagina aan
    assert response.status_code == 200  # Pagina moet succesvol laden
    assert b"<html" in response.data or b"index" in response.data  # HTML of inhoud van indexpagina moet aanwezig zijn

# ---- ROUTES MET DATABASE: MOCKING ----

# Test dat de klachtenlijstpagina werkt met een gemockte databaseverbinding
@patch("routes.klacht_routes.sqlite3.connect")  # Mock de databaseconnectie
def test_klachten_route(mock_connect, client):
    mock_cursor = MagicMock()  # Maak een nep-cursor
    mock_cursor.fetchall.return_value = [(1, "Hoofdpijn", "Pijn in het hoofd")]  # Nepresultaat voor klachten
    mock_connect.return_value.cursor.return_value = mock_cursor  # Zorg dat connect().cursor() deze mock geeft
    response = client.get("/klachten")  # Vraag de route `/klachten` op
    assert response.status_code == 200  # Pagina moet laden
    assert b"<html" in response.data or b"klachten" in response.data.lower()  # HTML of woord 'klachten' moet voorkomen

# Test dat de detailpagina voor een bestaande klacht goed werkt
@patch("routes.klacht_routes.sqlite3.connect")  # Mock databaseconnectie
def test_klacht_detail_route_bestaande_klacht(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Beschrijving van hoofdpijn")  # Nepresultaat voor klacht-id en beschrijving
    mock_cursor.fetchall.side_effect = [
        [("PlantA",)],  # Eerste fetchall() → gekoppelde_planten
        [(1, "PlantA")],  # Tweede fetchall() → alle_planten
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klacht/Hoofdpijn")  # Vraag klacht-detailpagina op
    assert response.status_code == 200  # Pagina moet bestaan
    assert b"<html" in response.data or b"hoofdpijn" in response.data.lower()  # Inhoud moet kloppen

# Test dat een niet-bestaande klacht een foutmelding toont
@patch("routes.klacht_routes.sqlite3.connect")  # Mock database
def test_klacht_detail_route_niet_bestaande_klacht(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # Geen resultaat = klacht bestaat niet
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klacht/GeenbestaandeKlacht")  # Vraag niet-bestaande klacht op
    assert response.status_code == 200  # HTML-pagina moet wel renderen
    assert b"niet gevonden" in response.data.lower()  # Verwacht foutmelding in pagina


# Test voor laden van klantenoverzicht
@patch("routes.klant_routes.sqlite3.connect")  # Mock databaseconnectie voor klant_routes
def test_klanten_route(mock_connect, client):
    mock_cursor = MagicMock()  # Maak een mock cursor
    mock_cursor.fetchall.return_value = [(1, "Testklant")]  # Simuleer een klant in de database
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klanten")  # Vraag de route /klanten op
    assert response.status_code == 200  # Pagina moet succesvol laden
    assert b"<html" in response.data or b"klanten" in response.data.lower()  # Check op inhoud of HTML

# Test detailweergave van klantgegevens
@patch("routes.klant_routes.sqlite3.connect")
def test_klant_detail_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "Testklant", "email", "telefoon", "adres")  # Klantgegevens
    mock_cursor.fetchall.side_effect = [[], [], [], [], []]  # Geen notities, afspraken, behandelingen, klachten, planten
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klant/1")  # Vraag detailpagina van klant ID 1 op
    assert response.status_code == 200
    assert b"<html" in response.data or b"klant" in response.data.lower()  # Check of pagina gerenderd is

# Test pagina met behandelingen per klant
@patch("routes.klant_routes.sqlite3.connect")
def test_klanten_behandelingen_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [
        [(1, "Testklant")],  # klantenlijst
        [(1, "Behandeling1", "2025-01-01")],  # laatste behandeling
        [("Hoofdpijn",)],  # klachten
        [("PlantA",)],  # planten
    ]
    mock_cursor.fetchone.side_effect = [(1, "Behandeling1", "2025-01-01")]  # behandeling_id, naam, datum
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/klanten/behandelingen")  # Vraag behandelingenoverzicht op
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()  # Check op inhoud

# Test POST-verzoek voor het aanmaken van een nieuwe klant
@patch("routes.klant_routes.sqlite3.connect")
def test_nieuwe_klant_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1  # Simuleer nieuw klant-ID
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(  # Simuleer POST-verzoek naar nieuwe klant
        "/nieuwe_klant",
        data={
            "naam": "Testklant",  # Klantnaam uit formulier
            "emailadres": "test@example.com",  # Email
            "telefoon": "0612345678",  # Telefoonnummer
            "adres": "Straat 1",  # Adres
        },
        follow_redirects=True,  # Volg redirect naar klantdetailpagina
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"klant" in response.data.lower()  # Check op HTML of klantpagina


# Test POST-verzoek om een notitie toe te voegen
# Test POST-verzoek voor het toevoegen van een notitie aan een klant
@patch("routes.klant_routes.sqlite3.connect")
def test_notitie_toevoegen_route_post(mock_connect, client):
    mock_cursor = MagicMock()  # Maak een mock cursor aan
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/notitie_toevoegen",  # Route voor notitie toevoegen bij klant 1
        data={"inhoud": "Testnotitie"},  # Gegevens uit het formulier
        follow_redirects=True,  # Volg redirect naar klantdetailpagina
    )
    assert response.status_code == 200  # Pagina moet succesvol laden
    assert b"<html" in response.data or b"notitie" in response.data.lower()  # Check of notitie of HTML voorkomt

# Test POST-verzoek om een behandeling met klachten en planten toe te voegen
@patch("routes.klant_routes.sqlite3.connect")
def test_nieuwe_behandeling_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1  # Simuleer ID van toegevoegde behandeling
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/nieuwe_behandeling",  # Route voor toevoegen behandeling
        data={
            "naam": "Testbehandeling",  # Naam van de behandeling
            "datum": "2025-01-01",  # Datum van de behandeling
            "klachten": ["1"],  # Gekoppelde klacht-ID's
            "planten": ["1"],  # Gekoppelde plant-ID's
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()  # Controleer op inhoud

# Test POST-verzoek voor het toevoegen van een losse behandelingstekst
@patch("routes.klant_routes.sqlite3.connect")
def test_behandeling_toevoegen_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/behandeling_toevoegen",  # Alternatieve route zonder koppelingen
        data={"behandeling": "Testbehandeling"},  # Alleen tekst
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()  # Controleer op inhoud

# Test POST-verzoek om bestaande behandelingstekst bij klant te updaten
@patch("routes.klant_routes.sqlite3.connect")
def test_update_behandeling_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/klant/1/update_behandeling",  # Route voor updaten van behandelingstekst
        data={"behandeling": "Update"},  # Nieuwe inhoud
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"behandeling" in response.data.lower()  # Check op inhoud of structuur

# Test POST om afspraak toe te voegen
# Test POST-verzoek voor het toevoegen van een nieuwe afspraak
@patch("routes.klant_routes.sqlite3.connect")
def test_nieuwe_afspraak_route_post(mock_connect, client):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/nieuwe_afspraak/1",  # Route voor het toevoegen van een afspraak aan klant met ID 1
        data={
            "datum": "2025-05-01",  # Datum van de afspraak
            "tijd": "10:00",  # Tijdstip van de afspraak
            "onderwerp": "Testafspraak",  # Onderwerp uit het formulier
            "locatie": "Praktijk",  # Locatie uit het formulier
        },
        follow_redirects=True,  # Volg de redirect naar klantdetailpagina
    )
    assert response.status_code == 200  # Pagina moet succesvol laden
    assert b"<html" in response.data or b"afspraak" in response.data.lower()  # Check op HTML of het woord 'afspraak'

# Test ophalen van plantenlijst
@patch("routes.plant_routes.sqlite3.connect")
def test_planten_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("PlantA",)]  # Simuleer een lijst met één plant
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/planten")  # Vraag route op die planten toont
    assert response.status_code == 200  # Response moet OK zijn
    assert b"<html" in response.data or b"plant" in response.data.lower()  # Check op HTML of het woord 'plant'

# Test detailweergave van een specifieke plant
@patch("routes.plant_routes.sqlite3.connect")
# Test GET-verzoek voor de informatieve route van een plant (bijv. /plant/PlantA/info)
def test_plant_info_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        ("PlantA", "Beschrijving", "Botanische naam", "bla", "bla", "bla", "bla", None),  # Plantgegevens
        (1,),  # Plant ID
    ]
    mock_cursor.description = [  # Gesimuleerde kolomnamen van de 'planten'-tabel
        ("naam",),
        ("beschrijving",),
        ("botanische_naam",),
        ("col4",),
        ("col5",),
        ("col6",),
        ("col7",),
        ("col8",),
    ]
    mock_cursor.fetchall.return_value = [("Hoofdpijn",)]  # Simuleer gekoppelde klacht
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/plant/PlantA/info")  # Vraag plant-info-pagina op
    assert response.status_code == 200
    assert b"<html" in response.data or b"plant" in response.data.lower()

# Test GET-verzoek voor het bewerken van een plant via de detailroute
@patch("routes.plant_routes.sqlite3.connect")
def test_plant_detail_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (1,),  # plant_id ophalen
        ("PlantA", "Beschrijving", "Botanische naam", "bla", "bla", "bla", "bla", None),  # plantgegevens
    ]
    mock_cursor.description = [  # Gesimuleerde kolommen
        ("naam",),
        ("beschrijving",),
        ("botanische_naam",),
        ("col4",),
        ("col5",),
        ("col6",),
        ("col7",),
        ("col8",),
    ]
    mock_cursor.fetchall.side_effect = [[(1, "Hoofdpijn")], [(1,)]]  # klachten en gekoppelde klachten
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.get("/plant/PlantA")  # Vraag de bewerkpagina van de plant op
    assert response.status_code == 200
    assert b"<html" in response.data or b"plant" in response.data.lower()

# Test POST-verzoek voor het koppelen van een plant aan een klacht
@patch("routes.plant_routes.sqlite3.connect")
def test_koppel_plant_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [None, ("Hoofdpijn",), (1, "Beschrijving")]  # Simuleer: geen bestaande koppeling, dan redirectdata
    mock_cursor.fetchall.side_effect = [[("PlantA",)], [(1, "PlantA")]]  # gekoppelde + alle planten
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/koppel_plant",  # Route om plant aan klacht te koppelen
        data={"klacht_id": "1", "plant_id": "1"},  # Formulierdata
        follow_redirects=True,  # Volg redirect naar klacht-detail
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"klacht" in response.data.lower()

# Test POST-verzoek voor het verwijderen van een koppeling tussen plant en klacht
@patch("routes.plant_routes.sqlite3.connect")
def test_verwijder_plant_route(mock_connect, client):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [(1,), ("Hoofdpijn",), (1, "Beschrijving")]  # plant_id, klachtnaam, klachtinfo
    mock_cursor.fetchall.side_effect = [[("PlantA",)], [(1, "PlantA")]]  # gekoppelde en alle planten
    mock_connect.return_value.cursor.return_value = mock_cursor
    response = client.post(
        "/verwijder_plant",  # Route om koppeling te verwijderen
        data={"plant_naam": "PlantA", "klacht_id": "1"},  # Formulierdata
        follow_redirects=True,  # Volg redirect naar klacht-detail
    )
    assert response.status_code == 200
    assert b"<html" in response.data or b"klacht" in response.data.lower()
