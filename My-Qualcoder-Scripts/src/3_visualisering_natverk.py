import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import os

filnamn = "data.qda"
bild_filnamn = "graf_natverk.png"

def over_lapp(start1, slut1, start2, slut2):
    return max(0, min(slut1, slut2) - max(start1, start2)) > 0

print("--- GENERERAR NÄTVERK ---")

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

        G = nx.Graph()
        
        for i in range(len(data)):
            if not G.has_node(data[i][0]): G.add_node(data[i][0])
            for j in range(i + 1, len(data)):
                k1, k2 = data[i], data[j]
                if k1[1] == k2[1] and k1[0] != k2[0]:
                    if over_lapp(k1[2], k1[3], k2[2], k2[3]):
                        if G.has_edge(k1[0], k2[0]):
                            G[k1[0]][k2[0]]['weight'] += 1
                        else:
                            G.add_edge(k1[0], k2[0], weight=1)

        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G, k=0.8, iterations=50)
        
        weights = [G[u][v]['weight'] for u,v in G.edges()]
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='#A0CBE2', alpha=0.9)
        nx.draw_networkx_edges(G, pos, width=weights, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.axis('off')
        plt.savefig(bild_filnamn, dpi=300)
        print(f"✅ Bild sparad: {bild_filnamn}")
        plt.show()

    except Exception as e:
        print(f"Fel: {e}")
