import sqlite3
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF

# --- INSTÄLLNINGAR ---
filnamn = "data.qda"
rapport_fil = "inspirations_förslag.txt"
antal_teman_att_hitta = 5  # Hur många "dolda ämnen" ska den leta efter?
antal_ord_per_tema = 10

# Lägg till svenska stoppord här om resultatet blir skräpigt
stoppord = ['och', 'att', 'det', 'som', 'en', 'ett', 'är', 'var', 'jag', 
            'vi', 'de', 'den', 'har', 'inte', 'om', 'på', 'av', 'med', 
            'för', 'till', 'men', 'då', 'så', 'kan', 'ska', 'alltså', 'eller', 'man', 'dom']

print("--- STARTAR INSPIRATIONS-GENERATORN ---")

if not os.path.exists(filnamn):
    print(f"Saknar filen '{filnamn}'.")
else:
    try:
        conn = sqlite3.connect(filnamn)
        cursor = conn.cursor()

        # Vi hämtar all text du hittills markerat/kodat
        # (Detta hjälper dig hitta mönster i det du redan tyckt var viktigt)
        query = "SELECT seltext FROM code_text"
        cursor.execute(query)
        resultat = cursor.fetchall()
        conn.close()

        texter = [rad[0] for rad in resultat]
        
        if len(texter) < 5:
            print("För lite data! Koda fler stycken först.")
        else:
            with open(rapport_fil, "w", encoding="utf-8") as f:
                
                # --- DEL 1: VANLIGA FRASER (N-GRAMS) ---
                # Hittar kombinationer av 2 eller 3 ord som återkommer
                f.write("=== VANLIGA FRASER (MÖJLIGA KODER?) ===\n")
                f.write("Dessa ordpar dyker ofta upp tillsammans:\n\n")
                
                vec = CountVectorizer(ngram_range=(2, 3), stop_words=stoppord, min_df=2)
                try:
                    bag_of_words = vec.fit_transform(texter)
                    sum_words = bag_of_words.sum(axis=0) 
                    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
                    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
                    
                    for word, freq in words_freq[:20]:
                        f.write(f"- \"{word}\" (Förekommer {freq} gånger)\n")
                except ValueError:
                    f.write("(För lite data för att hitta fraser ännu)\n")

                f.write("\n" + "="*40 + "\n\n")

                # --- DEL 2: TOPIC MODELING (NMF) ---
                # Försöker hitta "kluster" av ord som hör ihop (Teman)
                f.write(f"=== MATEMATISKA TEMAN (TOPIC MODELING) ===\n")
                f.write("Datorn har sorterat dina texter i grupper. Ser du något mönster?\n\n")

                tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words=stoppord)
                try:
                    tfidf = tfidf_vectorizer.fit_transform(texter)
                    nmf = NMF(n_components=antal_teman_att_hitta, random_state=1, init='nndsvd').fit(tfidf)
                    feature_names = tfidf_vectorizer.get_feature_names_out()

                    for topic_idx, topic in enumerate(nmf.components_):
                        f.write(f"TEMA FÖRSLAG {topic_idx + 1}: ")
                        top_words = [feature_names[i] for i in topic.argsort()[:-antal_ord_per_tema - 1:-1]]
                        f.write(", ".join(top_words) + "\n")
                except ValueError:
                     f.write("(För lite data eller unika ord för att modellera teman)\n")

            print(f"✅ Analys klar! Öppna filen: {rapport_fil}")
            print("Läs igenom 'Vanliga Fraser' - där hittar du ofta bra koder!")

    except Exception as e:
        print(f"Fel: {e}")

input("\nTryck Enter för att avsluta...")
