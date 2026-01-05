import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
bild_filnamn = "graf_sekvens.png"

print("--- ANALYSERAR SEKVENS & ORDNINGSFÖLJD ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # Hämta data SORTERAD på fil och position (Viktigt!)
        # Vi vill veta vad som hände först, sen senast.
        query = """
        SELECT code_text.fid, code_text.pos0, code_name.name
        FROM code_text 
        JOIN code_name ON code_text.cid = code_name.cid
        ORDER BY code_text.fid, code_text.pos0
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()

        transitions = []

        # Loopa igenom datan och hitta par (Vad händer nu -> Vad händer sen?)
        for i in range(len(data) - 1):
            fid_nu = data[i][0]
            kod_nu = data[i][2]
            
            fid_nasta = data[i+1][0]
            kod_nasta = data[i+1][2]

            # Vi räknar bara om det är samma intervju (fid)
            # och om koden faktiskt byter (inte samma kod två gånger i rad)
            if fid_nu == fid_nasta and kod_nu != kod_nasta:
                transitions.append((kod_nu, kod_nasta))

        print(f"Hittade {len(transitions)} ställen där samtalet bytte ämne.")

        if len(transitions) == 0:
            print("För lite data för att se sekvenser.")
        else:
            # Skapa Matris
            df = pd.DataFrame(transitions, columns=['Från', 'Till'])
            kors_tabell = pd.crosstab(df['Från'], df['Till'])

            # RITA HEATMAP
            plt.figure(figsize=(12, 10))
            sns.heatmap(kors_tabell, annot=True, fmt="d", cmap="Blues", linewidths=.5)
            
            plt.title('Vart leder samtalet? (Sekvensanalys)', fontsize=16)
            plt.ylabel('Om vi pratar om detta...', fontsize=12)
            plt.xlabel('...så byter vi oftast ämne till detta', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            plt.savefig(bild_filnamn, dpi=300)
            print(f"✅ Sekvenskarta sparad: {bild_filnamn}")
            plt.show()

    except Exception as e:
        print(f"Fel: {e}")
