import sqlite3
import plotly.graph_objects as go
import os

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
html_filnamn = "graf_sankey.html"

# Dina fasta nivå-2 koder (Så skriptet vet vad som är mitten)
fasta_koder = ['What', 'How', 'Why', 'Student', 'Teacher', 'Content', 
               'Instruction', 'Learning', 'Assessment', 'Environment', 
               'Interaction', 'Knowledge', 'Skills', 'Attitudes', 
               'Past', 'Present', 'Future', 'Intrinsic', 'Extrinsic', 
               'Transformational', 'Truth', 'Method', 'Belief']

def over_lapp(start1, slut1, start2, slut2):
    return max(0, min(slut1, slut2) - max(start1, start2)) > 0

print("--- GENERERAR SANKEY-DIAGRAM ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # Hämta kodnamn och deras tillhörande kategori (parent)
        # I QualCoder ligger kategorier i 'code_cat' tabellen ibland, 
        # men vi gör det enkelt: Vi tittar på överlappningar i texten.
        
        query = """
        SELECT code_name.name, code_text.fid, code_text.pos0, code_text.pos1
        FROM code_text 
        JOIN code_name ON code_text.cid = code_name.cid
        """
        cursor.execute(query)
        alla_kodningar = cursor.fetchall()
        conn.close()

        source = [] # Från
        target = [] # Till
        value = []  # Antal

        # Vi bygger en ordbok för att hålla koll på kopplingar
        # Struktur: { ("Kategori", "FastKod"): Antal, ("FastKod", "FriKod"): Antal }
        kopplingar = {}

        print(f"Analyserar {len(alla_kodningar)} kodningar...")

        for i in range(len(alla_kodningar)):
            kod1 = alla_kodningar[i]
            namn1 = kod1[0]
            
            # Vi letar efter andra koder som överlappar med denna
            for j in range(len(alla_kodningar)):
                if i == j: continue # Jämför inte med sig själv
                
                kod2 = alla_kodningar[j]
                namn2 = kod2[0]

                # Krav: Samma fil, överlappande text
                if kod1[1] == kod2[1] and over_lapp(kod1[2], kod1[3], kod2[2], kod2[3]):
                    
                    # LOGIK FÖR NIVÅERNA
                    # 1. KOPPLING: Kategori -> Fast Kod
                    # (Vi gissar att Kategorierna är de som INTE finns i listan 'fasta_koder'
                    # och INTE är de fria koderna. Detta är en förenkling.)
                    
                    # Här gör vi en smart koll: 
                    # Om Namn2 är en av dina 'What/How/Why' och Namn1 INTE är det...
                    # Då antar vi att Namn1 är Kategorin (t.ex. Classic Orientation)
                    if namn2 in fasta_koder and namn1 not in fasta_koder:
                        # Kolla så namn1 inte är en "Fri kod" (oftast mer specifik)
                        # För enkelhetens skull: Vi antar att din Hierarki i QualCoder är:
                        # Kategori (Mapp) -> Innehåller koder.
                        # Men eftersom vi bara har text-överlappning här:
                        pair = (namn1, namn2)
                        kopplingar[pair] = kopplingar.get(pair, 0) + 1

                    # 2. KOPPLING: Fast Kod -> Fri Kod
                    # Om Namn1 är Fast (Why) och Namn2 är något annat (Fri kod)
                    elif namn1 in fasta_koder and namn2 not in fasta_koder:
                        # Vi vill inte koppla tillbaka till Kategorin
                        # Så vi måste veta om Namn2 är en "Under-kod" eller "Över-kategori".
                        # I detta skript antar vi att allt som inte är Fast kod är Fri kod,
                        # om det inte redan identifierats som kategori. 
                        # (Detta kan bli lite rörigt om man inte är strikt, men vi testar!)
                        pair = (namn1, namn2)
                        kopplingar[pair] = kopplingar.get(pair, 0) + 1

        # Förbered data för Plotly
        # Vi måste göra om alla namn till siffror (index)
        alla_unika_namn = list(set([k[0] for k in kopplingar.keys()] + [k[1] for k in kopplingar.keys()]))
        namn_till_id = {namn: i for i, namn in enumerate(alla_unika_namn)}

        for (fran, till), antal in kopplingar.items():
            # Vi delar antalet på 2 eftersom överlappning räknas dubbelt i loopen
            riktigt_antal = antal / 2 
            if riktigt_antal >= 1: # Visa bara om det finns minst 1 koppling
                source.append(namn_till_id[fran])
                target.append(namn_till_id[till])
                value.append(riktigt_antal)

        # Rita Diagrammet
        fig = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 15,
              thickness = 20,
              line = dict(color = "black", width = 0.5),
              label = alla_unika_namn,
              color = "blue"
            ),
            link = dict(
              source = source,
              target = target,
              value = value
          ))])

        fig.update_layout(title_text="Kod-Flöde: Kategori -> Fast -> Fri", font_size=10)
        fig.write_html(html_filnamn)
        
        print(f"✅ Interaktivt diagram sparat: {html_filnamn}")
        print("Öppna filen i din webbläsare!")

    except Exception as e:
        print(f"Fel: {e}")
