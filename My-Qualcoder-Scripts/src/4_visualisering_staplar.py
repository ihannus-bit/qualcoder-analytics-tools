import sqlite3
import os
from collections import Counter
import matplotlib.pyplot as plt

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
bild_filnamn = "graf_staplar.png"

print("--- RITAR STAPELDIAGRAM ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()
        
        # Hämta kodnamn
        query = "SELECT code_name.name FROM code_text JOIN code_name ON code_text.cid = code_name.cid"
        cursor.execute(query)
        resultat = cursor.fetchall()
        conn.close()

        # Räkna
        alla_teman = [rad[0] for rad in resultat]
        statistik = Counter(alla_teman)

        # Ta fram topp 10
        sorterad_data = statistik.most_common(10)
        teman = [rad[0] for rad in sorterad_data]
        antal = [rad[1] for rad in sorterad_data]

        # Rita
        plt.figure(figsize=(10, 6))
        plt.bar(teman, antal, color='#66b3ff', edgecolor='black')

        plt.title('Topp 10 Vanligaste Teman', fontsize=16)
        plt.xlabel('Tema', fontsize=12)
        plt.ylabel('Antal', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(bild_filnamn, dpi=300)
        print(f"✅ Graf sparad: {bild_filnamn}")
        plt.show()

    except Exception as e:
        print(f"Fel: {e}")
