import sqlite3
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

filnamn = "data.qda"
bild_filnamn = "graf_heatmap.png"

def over_lapp(start1, slut1, start2, slut2):
    return max(0, min(slut1, slut2) - max(start1, start2)) > 0

print("--- GENERERAR HEATMAP ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()
        query = "SELECT code_name.name, code_text.fid, code_text.pos0, code_text.pos1 FROM code_text JOIN code_name ON code_text.cid = code_name.cid"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()

        # Skapa matris
        unika = sorted(list(set([rad[0] for rad in data])))
        matrix = pd.DataFrame(0, index=unika, columns=unika)

        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                k1, k2 = data[i], data[j]
                if k1[1] == k2[1] and k1[0] != k2[0]:
                    if over_lapp(k1[2], k1[3], k2[2], k2[3]):
                        matrix.loc[k1[0], k2[0]] += 1
                        matrix.loc[k2[0], k1[0]] += 1

        plt.figure(figsize=(12, 10))
        sns.heatmap(matrix, annot=True, fmt="d", cmap='YlOrRd', linewidths=.5)
        plt.title('Sambands-Heatmap', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(bild_filnamn, dpi=300)
        print(f"✅ Bild sparad: {bild_filnamn}")
        plt.show()

    except Exception as e:
        print(f"Fel: {e}")
