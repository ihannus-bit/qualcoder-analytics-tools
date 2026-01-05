import sqlite3
import os

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
rapport_fil = "tacknings_rapport.txt"
min_langd_pa_hal = 100  # Visa bara okodade stycken längre än 100 tecken

print("--- STARTAR GAP-ANALYS (TÄCKNINGSKOLL) ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # Hämta alla filer
        cursor.execute("SELECT id, name, fulltext FROM source")
        kallor = cursor.fetchall()

        total_text_len = 0
        total_coded_len = 0

        with open(rapport_fil, "w", encoding="utf-8") as f:
            f.write("=== RAPPORT ÖVER OKODAT MATERIAL ===\n")
            f.write("Här listas textstycken som INTE har fått någon kod än.\n")
            f.write("Använd detta för att hitta teman du missat.\n\n")

            for fil_id, fil_namn, text in kallor:
                if not text: continue
                text_len = len(text)
                total_text_len += text_len

                # Hämta alla kodningar för denna fil (start och slut)
                cursor.execute("SELECT pos0, pos1 FROM code_text WHERE fid=?", (fil_id,))
                kodningar = cursor.fetchall()

                # Skapa en lista med "täckta" intervall
                # Vi måste slå ihop överlappande intervall för att räkna rätt
                intervall = sorted(kodningar)
                merged = []
                if intervall:
                    curr_start, curr_end = intervall[0]
                    for next_start, next_end in intervall[1:]:
                        if next_start < curr_end:  # Överlappning
                            curr_end = max(curr_end, next_end)
                        else:
                            merged.append((curr_start, curr_end))
                            curr_start, curr_end = next_start, next_end
                    merged.append((curr_start, curr_end))

                # Räkna kodad längd
                coded_len = sum(end - start for start, end in merged)
                total_coded_len += coded_len
                
                procent = (coded_len / text_len) * 100
                f.write(f"FIL: {fil_namn} (Täckning: {procent:.1f}%)\n")
                f.write("-" * 40 + "\n")

                # HITTA HÅLEN (Gaps)
                nuvarande_pos = 0
                hittade_hal = 0
                
                # Lägg till slutpunkten på texten som ett "fiktivt" intervall
                merged.append((text_len, text_len))

                for start, end in merged:
                    # Om det finns ett glapp mellan nuvarande pos och nästa start
                    gap_len = start - nuvarande_pos
                    
                    if gap_len > min_langd_pa_hal:
                        hal_text = text[nuvarande_pos:start].strip()
                        # Visa bara om det inte är tomt
                        if hal_text:
                            f.write(f"[RAD {nuvarande_pos}-{start}] OKODAT:\n")
                            f.write(f"\"{hal_text}\"\n\n")
                            hittade_hal += 1
                    
                    nuvarande_pos = max(nuvarande_pos, end)

                if hittade_hal == 0:
                    f.write("(Inga stora okodade partier hittades)\n")
                f.write("\n" + "="*40 + "\n\n")

        conn.close()

        total_tackning = (total_coded_len / total_text_len) * 100 if total_text_len > 0 else 0
        
        print(f"✅ Analys klar!")
        print(f"Total täckningsgrad: {total_tackning:.1f}%")
        print(f"Rapport sparad i: {rapport_fil}")
        print("Läs rapporten för att se vad du missat!")

    except Exception as e:
        print(f"Fel: {e}")
