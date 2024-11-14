# app.py
from flask import Flask, render_template, request, jsonify
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
import random

app = Flask(__name__)

# Load the crawled data
with open('hasil_crawl.json', 'r', encoding='utf-8') as f:
    crawled_data = json.load(f)

# Load the TF-IDF index
with open('tfidf_index.json', 'r', encoding='utf-8') as f:
    tfidf_index = json.load(f)

def extract_tags(content):
    # Simple tag extraction based on common categories in the content
    common_categories = ['Penyakit', 'Kesehatan', 'Kecantikan', 'Gizi', 'Olahraga', 'Lifestyle']
    found_tags = []
    
    for category in common_categories:
        if category.lower() in content.lower():
            found_tags.append(category)
    
    return found_tags[:3]  # Limit to 3 tags

def prepare_article_data(articles):
    prepared_articles = []
    for article in articles:
        if article['title'] and article['content']:
            tags = extract_tags(article['content'])
            prepared_articles.append({
                'title': article['title'].strip(),
                'url': article['url'],
                'content': article['content'].strip(),
                'tags': tags or ['Artikel']  # Default tag if none found
            })
    # Shuffle the articles to get random ones each time
    random.shuffle(prepared_articles)
    return prepared_articles


def calculate_cosine_similarity(query_vector, document_vector):
    # Buat set dari semua term yang ada di kedua vektor
    all_terms = set(query_vector.keys()) | set(document_vector.keys())
    
    # Buat vektor dengan dimensi yang sama untuk query dan dokumen
    query_array = np.array([query_vector.get(term, 0) for term in all_terms])
    doc_array = np.array([document_vector.get(term, 0) for term in all_terms])
    
    # Reshape vektor menjadi 2D array
    query_array = query_array.reshape(1, -1)
    doc_array = doc_array.reshape(1, -1)
    
    # Hitung cosine similarity
    return cosine_similarity(query_array, doc_array)[0][0]

def calculate_jaccard_similarity(query_terms, document_terms):
    query_set = set(query_terms.keys())
    doc_set = set(document_terms.keys())
    
    intersection = len(query_set.intersection(doc_set))
    union = len(query_set.union(doc_set))
    
    return intersection / union if union != 0 else 0

def search(query, method='cosine'):
    # Create query vector using same terms as in documents
    query_terms = query.lower().split()
    query_vector = defaultdict(float)
    
    # Create simple TF for query
    for term in query_terms:
        query_vector[term] += 1
    
    results = []
    
    for url, doc_vector in tfidf_index.items():
        if method == 'cosine':
            similarity = calculate_cosine_similarity(query_vector, doc_vector)
        else:  # jaccard
            similarity = calculate_jaccard_similarity(query_vector, doc_vector)
            
        # Find matching document in crawled data
        doc_data = next((doc for doc in crawled_data if doc['url'] == url), None)
        
        if doc_data and similarity > 0:
            results.append({
                'url': url,
                'title': doc_data.get('title', ''),
                'content': doc_data.get('content', '')[:200] + '...',  # Preview
                'score': similarity
            })
    
    # Sort by similarity score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]  # Return top 10 results

@app.route('/')
def home():
    # Prepare articles for homepage
    articles = prepare_article_data(crawled_data)
    return render_template('index.html', articles=articles)

@app.route('/search')
def search_results():
    query = request.args.get('q', '')
    method = request.args.get('method', 'cosine')
    
    if not query:
        return render_template('index.html')
    
    results = search(query, method)
    return render_template('result.html', query=query, results=results, method=method)

if __name__ == '__main__':
    app.run(debug=True)