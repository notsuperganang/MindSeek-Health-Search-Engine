import json
import math
from collections import Counter

# Path file untuk indeks invert dan TF-IDF
inverted_index_file = r'/home/notsuperganang/Documents/Kuliah/Semester 5/PI/MK/project-UAS/project/mycrawler/mycrawler/inverted_index.json'
tfidf_index_file = r'/home/notsuperganang/Documents/Kuliah/Semester 5/PI/MK/project-UAS/project/mycrawler/mycrawler/tfidf_index.json'

# Membaca indeks dari file JSON
with open(inverted_index_file, 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

with open(tfidf_index_file, 'r', encoding='utf-8') as f:
    tfidf_index = json.load(f)

# Daftar stop words sederhana
stop_words = set([
    "dan", "atau", "di", "ke", "dari", "untuk", "yang", "adalah", "pada", "dengan"
])

# Fungsi untuk menghitung Cosine Similarity
def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
    query_magnitude = math.sqrt(sum(value ** 2 for value in query_vector.values()))
    doc_magnitude = math.sqrt(sum(value ** 2 for value in doc_vector.values()))
    if query_magnitude == 0 or doc_magnitude == 0:
        return 0.0
    return dot_product / (query_magnitude * doc_magnitude)

# Fungsi untuk menghitung Jaccard Similarity
def jaccard_similarity(query_terms, doc_terms):
    query_set = set(query_terms)
    doc_set = set(doc_terms)
    intersection = query_set.intersection(doc_set)
    union = query_set.union(doc_set)
    return len(intersection) / len(union) if union else 0

# Fungsi untuk preprocessing query
def preprocess_query(query):
    terms = query.lower().split()
    return [word for word in terms if word not in stop_words]

# Fungsi pencarian
def search_documents(query):
    query_terms = preprocess_query(query)

    # Menghitung vektor TF-IDF untuk query
    query_vector = Counter(query_terms)
    query_length = len(query_terms)
    N = len(tfidf_index)
    for term in query_vector:
        df = len(inverted_index.get(term, []))
        idf = math.log(N / df) if df else 0
        query_vector[term] = (query_vector[term] / query_length) * idf

    # Menyimpan hasil pencarian untuk Cosine dan Jaccard
    cosine_results = []
    jaccard_results = []

    # Periksa dokumen yang relevan berdasarkan indeks invert
    doc_candidates = set()
    for term in query_terms:
        if term in inverted_index:
            doc_candidates.update(inverted_index[term])

    # Proses setiap dokumen kandidat
    for doc_id in doc_candidates:
        doc_vector = tfidf_index[doc_id]
        
        # Cosine Similarity
        cos_sim = cosine_similarity(query_vector, doc_vector)
        cosine_results.append((doc_id, cos_sim))
        
        # Jaccard Similarity
        doc_terms = doc_vector.keys()
        jac_sim = jaccard_similarity(query_terms, doc_terms)
        jaccard_results.append((doc_id, jac_sim))
    
    # Urutkan hasil dan ambil 10 dokumen teratas untuk setiap metode
    cosine_results = sorted(cosine_results, key=lambda x: x[1], reverse=True)[:10]
    jaccard_results = sorted(jaccard_results, key=lambda x: x[1], reverse=True)[:10]
    
    return cosine_results, jaccard_results

# Contoh penggunaan
query = "makanan untuk diet"
cosine_results, jaccard_results = search_documents(query)

# Tampilkan hasil
print("Hasil Pencarian Berdasarkan Cosine Similarity:")
for doc_id, score in cosine_results:
    print(f"Dokumen {doc_id}: Skor {score:.4f}")

print("\nHasil Pencarian Berdasarkan Jaccard Similarity:")
for doc_id, score in jaccard_results:
    print(f"Dokumen {doc_id}: Skor {score:.4f}")
