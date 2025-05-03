from flask import Blueprint, render_template, request, redirect, url_for, session

index_bp = Blueprint('index_bp', __name__)

ADMIN_GEBRUIKER = "admin"
ADMIN_WACHTWOORD = "test123"


@index_bp.route('/')
def index():
    if 'gebruiker' not in session:
        return redirect(url_for('index_bp.login'))
    return render_template('index.html')

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    foutmelding = None
    if request.method == 'POST':
        gebruikersnaam = request.form['gebruikersnaam']
        wachtwoord = request.form['wachtwoord']

        if gebruikersnaam == ADMIN_GEBRUIKER and wachtwoord == ADMIN_WACHTWOORD:
            session['gebruiker'] = gebruikersnaam
            return redirect(url_for('index_bp.index'))
        else:
            foutmelding = "Onjuiste gebruikersnaam of wachtwoord."

    return render_template('login.html', foutmelding=foutmelding)

@index_bp.route('/registreren')
def registreren():
    return "<h2>Registratiepagina komt nog!</h2><p><a href='/login'>← Terug naar login</a></p>"


@index_bp.route('/logout')
def logout():
    session.pop('gebruiker', None)
    return redirect(url_for('index_bp.login'))

