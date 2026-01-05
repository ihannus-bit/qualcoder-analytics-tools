import sqlite3
import matplotlib.pyplot as plt
import os

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
bild_filnamn = "graf_tidslinje.png"

print("--- RITAR NARRATIV TIDSLINJE ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # 1. Vi måste veta hur lång varje fil är för att kunna räkna ut %
        # Vi gissar längden genom att hitta den sista kodningen i varje fil
        cursor.execute("SELECT fid, MAX(pos1) FROM code_text GROUP BY fid")
        fil_langder = dict(cursor.fetchall())

        # 2. Hämta alla kodningar
        query = """
        SELECT code_name.name, code_text.fid, code_text.pos0 
        FROM code_text 
        JOIN code_name ON code_text.cid = code_name.cid
        """
        cursor.execute(query)
        alla_kodningar = cursor.fetchall()
        conn.close()

        # 3. Räkna ut relativ position (0.0 till 1.0) för varje kod
        x_values = [] # Position (0-100%)
        y_values = [] # Temat
        colors = []

        # Vi sorterar så att de vanligaste temana hamnar överst i grafen
        # (Lite snyggare så)
        from collections import Counter
        vanligaste = [x[0] for x in Counter([r[0] for r in alla_kodningar]).most_common(15)]
        
        print(f"Analyserar spridning för {len(vanligaste)} teman...")

        for kod in alla_kodningar:
            namn = kod[0]
            fid = kod[1]
            start_pos = kod[2]

            # Om koden tillhör topp-listan och vi vet filens längd
            if namn in vanligaste and fid in fil_langder:
                total_langd = fil_langder[fid]
                if total_langd > 0:
                    relativ_pos = (start_pos / total_langd) * 100 # Blir 0 till 100
                    
                    x_values.append(relativ_pos)
                    y_values.append(namn)

        # 4. RITA GRAFEN
        plt.figure(figsize=(12, 8))
        
        # En "Scatter plot" sätter en prick för varje förekomst
        plt.scatter(x_values, y_values, alpha=0.5, color='teal', s=100, marker='|')

        plt.title('Var i intervjuerna dyker temana upp?', fontsize=16)
        plt.xlabel('Intervjuns gång (0% = Start, 100% = Slut)', fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.7) # Hjälplinjer
        
        # Sätt fast ordningen på Y-axeln så den inte hoppar runt
        plt.yticks(fontsize=10)
        plt.tight_layout()

        plt.savefig(bild_filnamn, dpi=300)
        print(f"✅ Tidslinje sparad: {bild_filnamn}")
        plt.show()

    except Exception as e:
        print(f"Fel: {e}")
