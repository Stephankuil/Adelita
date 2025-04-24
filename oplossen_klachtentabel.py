import sqlite3

conn = sqlite3.connect("fytotherapie.db")
cursor = conn.cursor()

# Haal alle unieke klachten op, hoofdletterongevoelig
cursor.execute("SELECT DISTINCT LOWER(naam) as naam FROM klachten")
klachten_result = cursor.fetchall()

# Zet in lijst
klachten_in_db = sorted(set([r[0] for r in klachten_result]))

conn.close()

# Print of gebruik
for klacht in klachten_in_db:
    print(klacht)
