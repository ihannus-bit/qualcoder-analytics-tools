import sqlite3
import os
from collections import Counter
import re

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
rapport_fil = "drilldown_analys.txt"

# VILKEN KOD VILL DU RÖNTGA? (Ändra denna för att undersöka olika koder)
fokus_kod = "Why" 

# Svenska stoppord
stoppord = ['och', 'att', 'det', 'som', 'en', 'ett', 'är', 'var', 'jag', 
            'vi', 'de', 'den', 'har', 'inte', 'om', 'på', 'av', 'med', 
            'för', 'till', 'men', 'då', 'så', 'kan', 'ska', 'alltså', 'eller']

print(f"--- ANALYSERAR INNEHÅLLET I '{fokus_kod}' ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # 1. Hämta text som är kodad med din fokus-kod
        query = """
        SELECT code_text.seltext 
        FROM code_text 
        JOIN code_name ON code_text.cid = code_name.cid
        WHERE code_name.name = ?
        """
        cursor.execute(query, (fokus_kod,))
        resultat = cursor.fetchall()
        conn.close()

        texter = [rad[0] for rad in resultat]
        
        print(f"Hittade {len(texter)} textstycken kodade med '{fokus_kod}'.")

        if len(texter) == 0:
            print("Ingen data hittad. Kontrollera stavningen på koden (stor/liten bokstav).")
        else:
            # Slå ihop all text
            all_text = " ".join(texter).lower()
            
            # Ta bort punkt, komma osv
            all_text = re.sub(r'[^\w\s]', '', all_text)
            
            # Dela upp i ord
            orden = all_text.split()
            
            # Filtrera bort stoppord och korta ord
            rena_ord = [ordet for ordet in orden if ordet not in stoppord and len(ordet) > 3]
            
            # Räkna
            frekvens = Counter(rena_ord)

            # Spara rapport
            with open(rapport_fil, "w", encoding="utf-8") as f:
                f.write(f"=== INNEHÅLLSANALYS AV KODEN: {fokus_kod.upper()} ===\n")
                f.write(f"Baserat på {len(texter)} kodade segment.\n\n")
                
                f.write("TOPP 20 MENINGSBÄRANDE ORD (Potentiella underkoder):\n")
                f.write("---------------------------------------------------\n")
                for ordet, antal in frekvens.most_common(20):
                    f.write(f"- {ordet} ({antal} ggr)\n")
                
                f.write("\n\nEXEMPEL PÅ KONTEXT (De 3 längsta citaten):\n")
                # Sortera citat efter längd för att få kontext
                langa_citat = sorted(texter, key=len, reverse=True)[:3]
                for i, citat in enumerate(langa_citat, 1):
                    f.write(f"\n{i}. \"{citat.strip()}\"\n")

            print(f"✅ Analys klar! Öppna: {rapport_fil}")
            print("Orden i listan är förslag på dina nya 'Fria koder'.")

    except Exception as e:
        print(f"Fel: {e}")
