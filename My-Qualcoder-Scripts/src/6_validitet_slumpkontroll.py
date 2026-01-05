import sqlite3
import random
import os

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
rapport_fil = "validitets_kontroll.txt"
antal_stickprov = 5  # Hur många citat per kod vill du kontrollera?

print("--- STARTAR RANDOM AUDIT (BIAS-KONTROLL) ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # Hämta alla koder och deras texter
        query = """
        SELECT code_name.name, code_text.seltext 
        FROM code_text 
        JOIN code_name ON code_text.cid = code_name.cid
        """
        cursor.execute(query)
        alla_data = cursor.fetchall()
        conn.close()

        # Organisera datan per kod
        kod_bibliotek = {}
        for rad in alla_data:
            kodnamn = rad[0]
            text = rad[1]
            if kodnamn not in kod_bibliotek:
                kod_bibliotek[kodnamn] = []
            kod_bibliotek[kodnamn].append(text)

        print(f"Granskar {len(kod_bibliotek)} olika teman...")

        with open(rapport_fil, "w", encoding="utf-8") as f:
            f.write("=== VALIDITETSKONTROLL: SLUMPMÄSSIGT URVAL ===\n")
            f.write("Syfte: Läs igenom dessa stickprov. Är kodningen konsekvent?\n\n")

            for kod, texter in kod_bibliotek.items():
                f.write(f"--------------------------------------------------\n")
                f.write(f"TEMA: {kod.upper()} (Totalt {len(texter)} st)\n")
                f.write(f"--------------------------------------------------\n")
                
                # Ta slumpmässiga stickprov (eller alla om de är få)
                if len(texter) <= antal_stickprov:
                    urval = texter
                else:
                    urval = random.sample(texter, antal_stickprov)
                
                for i, citat in enumerate(urval, 1):
                    # Städa texten lite (ta bort radbrytningar)
                    ren_text = citat.replace('\n', ' ').strip()
                    f.write(f"{i}. \"{ren_text}\"\n")
                
                f.write("\n")

        print(f"✅ Stickprov sparade i: {rapport_fil}")
        print("Öppna filen och granska dina kodningar kritiskt!")

    except Exception as e:
        print(f"Fel: {e}")
