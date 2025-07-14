import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os

# 🔐 Laad omgevingsvariabelen
load_dotenv()

# 📦 Databaseconfiguratie uit .env
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# 🔐 Haal admin logingegevens uit .env
admin_gebruiker = os.getenv("ADMIN_GEBRUIKER")
admin_wachtwoord = os.getenv("ADMIN_WACHTWOORD")

if not admin_gebruiker or not admin_wachtwoord:
    raise ValueError("ADMIN_GEBRUIKER en/of ADMIN_WACHTWOORD ontbreekt in .env")

# 🔑 Genereer bcrypt-hash
wachtwoord_hash = bcrypt.hashpw(admin_wachtwoord.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# 💾 Verbind en controleer/invoegen
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Check of gebruiker al bestaat
cursor.execute("SELECT id FROM gebruikers WHERE gebruikersnaam = %s", (admin_gebruiker,))
if cursor.fetchone():
    print(f"⏩ Gebruiker '{admin_gebruiker}' bestaat al. Geen nieuwe invoer gedaan.")
else:
    cursor.execute("""
        INSERT INTO gebruikers (gebruikersnaam, wachtwoord_hash, rol)
        VALUES (%s, %s, %s)
    """, (admin_gebruiker, wachtwoord_hash, "admin"))
    conn.commit()
    print(f"✅ Gebruiker '{admin_gebruiker}' succesvol toegevoegd.")

cursor.close()
conn.close()
