from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Startpagina
@app.route('/')
def index():
    return render_template('index.html')

# Pagina met alle planten
@app.route('/planten')
def planten():
    conn = sqlite3.connect('fytotherapie.db')
    cursor = conn.cursor()
    cursor.execute("SELECT naam FROM planten ORDER BY naam ASC")
    planten_lijst = cursor.fetchall()
    conn.close()
    return render_template('planten.html', planten=planten_lijst)

if __name__ == '__main__':
    app.run(debug=True)
