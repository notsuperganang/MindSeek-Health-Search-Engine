import json
import math
from collections import defaultdict, Counter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Muat data dari file JSON
file_path = r'F:\semester 5\PI\project\mycrawler\mycrawler\hasil_crawl.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Inisialisasi stemmer untuk bahasa Indonesia
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Preprocessing: Stop words bahasa Indonesia
stop_words = {
    "yang", "di", "ke", "dari", "dan", "ini", "itu", "dengan", "untuk", "atau", "pada", "adalah",
    "dalam", "oleh", "akan", "sebagai", "sangat", "juga", "tidak", "karena", "bagi", "hanya", "kita",
    "saya", "kamu", "kami", "kalian", "mereka", "beliau", "ada", "akan", "bisa", "bukan", "harus",
    "apakah", "apa", "agar", "tersebut", "demikian", "tetapi", "supaya", "sedangkan", "serta", "namun",
    "antara", "itu", "sebuah", "setelah", "sekitar", "selalu", "sejak", "sedang", "masih", "pun",
    "pernah", "maka", "seperti", "sampai", "tanpa", "yaitu", "selain", "belum", "perlu", "kapan",
    "dimana", "bagaimana", "siapa", "dalam", "demi", "jika", "jikalau", "manakala", "seusai",
    "sebelum", "sehabis", "ketika", "dimana", "terus", "saja", "atau", "bahwa", "sebab", "lalu", "baik"
}


# Fungsi preprocessing (tokenisasi, penghilangan stop words, stemming)
def preprocess(text):
    # Tokenisasi dan konversi ke huruf kecil
    tokens = text.lower().split()
    # Penghilangan stop words dan stemming
    return [stemmer.stem(word) for word in tokens if word not in stop_words]

# Struktur data untuk indeks invert dan indeks TF-IDF
inverted_index = defaultdict(set)  # Gunakan set untuk menghindari duplikasi
tfidf_index = defaultdict(dict)

# Hitung DF (Document Frequency) untuk setiap term
df = Counter()
N = len(data)  # Jumlah total dokumen

# Memproses setiap dokumen
for doc in data:
    doc_id = doc['url']  # Gunakan URL sebagai identifier unik
    content = doc['content']
    
    # Preprocessing
    terms = preprocess(content)
    
    # Menghitung TF (Term Frequency)
    term_counts = Counter(terms)
    doc_length = len(terms)
    
    # Update indeks invert
    for term in set(terms):
        inverted_index[term].add(doc_id)  # Tambah doc_id ke set untuk menghindari duplikasi
        df[term] += 1
    
    # Hitung TF-IDF untuk setiap term
    for term, count in term_counts.items():
        tf = count / doc_length
        idf = math.log(N / df[term]) if df[term] else 0
        tfidf_index[doc_id][term] = tf * idf

# Konversi defaultdict ke dict sebelum menyimpan
inverted_index = {term: list(docs) for term, docs in inverted_index.items()}
tfidf_index = dict(tfidf_index)

# Menyimpan hasil indeks invert dan TF-IDF ke file JSON
inverted_index_file = r'F:\semester 5\PI\project\mycrawler\mycrawler\inverted_index.json'
tfidf_index_file = r'F:\semester 5\PI\project\mycrawler\mycrawler\tfidf_index.json'

# Menyimpan indeks invert ke file JSON
with open(inverted_index_file, 'w', encoding='utf-8') as f:
    json.dump(inverted_index, f, ensure_ascii=False, indent=4)

# Menyimpan indeks TF-IDF ke file JSON
with open(tfidf_index_file, 'w', encoding='utf-8') as f:
    json.dump(tfidf_index, f, ensure_ascii=False, indent=4)

print("Indeks invert dan TF-IDF telah disimpan ke file JSON.")
