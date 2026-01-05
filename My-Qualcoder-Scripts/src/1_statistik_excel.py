import sqlite3
import os
import csv
from collections import Counter

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"  # OBS: Döp din riktiga fil till detta!
csv_frekvens = "resultat_frekvens.csv"
csv_samband = "resultat_samband.csv"

def over_lapp(start1, slut1, start2, slut2):
    return max(0, min(slut1, slut2) - max(start1, start2)) > 0

print(f"--- STARTAR ANALYS AV {filnamn} ---")

if not os.path.exists(filnamn):
    print(f"FEL: Hittar inte '{filnamn}'. Lägg din .qda-fil i denna mapp och döp om den.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # Hämta data
        query = """
        SELECT code_name.name, code_text.fid, code_text.pos0, code_text.pos1, code_text.seltext
        FROM code_text 
        JOIN code_name ON code_text.cid = code_name.cid
        """
        cursor.execute(query)
        alla_kodningar = cursor.fetchall()
        conn.close()

        print(f"Hittade {len(alla_kodningar)} kodningar.")

        # DEL 1: FREKVENS (Räkna antal)
        alla_teman = [rad[0] for rad in alla_kodningar]
        frekvens = Counter(alla_teman)

        with open(csv_frekvens, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Tema', 'Antal träffar'])
            for tema, antal in frekvens.most_common():
                writer.writerow([tema, antal])
        print(f"✅ Statistik sparad till: {csv_frekvens}")

        # DEL 2: SAMBAND (Överlappningar)
        samband_lista = []
        for i in range(len(alla_kodningar)):
            k1 = alla_kodningar[i]
            for j in range(i + 1, len(alla_kodningar)):
                k2 = alla_kodningar[j]
                
                # Samma fil, olika kodnamn, överlappar
                if k1[1] == k2[1] and k1[0] != k2[0]:
                    if over_lapp(k1[2], k1[3], k2[2], k2[3]):
                        par = sorted([k1[0], k2[0]])
                        samband_lista.append(f"{par[0]} <--> {par[1]}")

        samband_counts = Counter(samband_lista)
        
        with open(csv_samband, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Tema 1', 'Tema 2', 'Antal överlappningar'])
            for par, antal in samband_counts.most_common():
                t1, t2 = par.split(" <--> ")
                writer.writerow([t1, t2, antal])
        print(f"✅ Sambandsanalys sparad till: {csv_samband}")

    except Exception as e:
        print(f"Ett fel uppstod: {e}")

input("\nTryck Enter för att avsluta...")
