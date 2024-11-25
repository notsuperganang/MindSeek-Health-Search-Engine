from flask import Flask, render_template, request, jsonify
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Download semua resource NLTK yang dibutuhkan
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

app = Flask(__name__)

# Load the crawled data
with open('data/hasil_crawl.json', 'r', encoding='utf-8') as f:
    crawled_data = json.load(f)

# Load the TF-IDF index
with open('output_indices/tfidf_index.json', 'r', encoding='utf-8') as f:
    tfidf_index = json.load(f)

# Di bagian awal file, tambahkan:
with open('output_indices/tags_index.json', 'r', encoding='utf-8') as f:
    tags_index = json.load(f)
    
def parse_date(date_str):
    if date_str == "Tanggal tidak tersedia":
        return datetime.min
    try:
        return datetime.strptime(date_str, "%d %B %Y")
    except:
        return datetime.min

def clean_text(text):
    # Lowercase the text
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    return text

# Modifikasi fungsi prepare_article_data:
def prepare_article_data(articles, page=1, per_page=9):
    prepared_articles = []
    for article in articles:
        if article['title'] and article['content']:
            image_url = article['image_url']
            if image_url == "URL gambar tidak tersedia":
                image_url = "https://via.placeholder.com/400x200"
            
            # Get tags from index instead of extracting
            tags = tags_index.get(article['url'], ['Artikel'])
            
            prepared_articles.append({
                'title': article['title'].strip(),
                'url': article['url'],
                'content': article['content'].strip(),
                'tags': tags,
                'image_url': image_url,
                'date': article['date']
            })
    
    # Sort articles by date (newest first)
    prepared_articles.sort(key=lambda x: parse_date(x['date']), reverse=True)
    
    # Calculate total pages
    total_articles = len(prepared_articles)
    total_pages = (total_articles + per_page - 1) // per_page
    
    # Get articles for current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Add pagination range
    if total_pages <= 10:
        page_range = range(1, total_pages + 1)
    else:
        if page <= 5:
            page_range = range(1, 11)
        elif page > total_pages - 5:
            page_range = range(total_pages - 9, total_pages + 1)
        else:
            page_range = range(page - 4, page + 6)
            
    return {
        'articles': prepared_articles[start_idx:end_idx],
        'total_pages': total_pages,
        'current_page': page,
        'has_next': page < total_pages,
        'total_articles': total_articles,
        'page_range': list(page_range)  # Add this
    }

def calculate_cosine_similarity(query_vector, document_vector):
    all_terms = set(query_vector.keys()) | set(document_vector.keys())
    query_array = np.array([query_vector.get(term, 0) for term in all_terms])
    doc_array = np.array([document_vector.get(term, 0) for term in all_terms])
    query_array = query_array.reshape(1, -1)
    doc_array = doc_array.reshape(1, -1)
    return cosine_similarity(query_array, doc_array)[0][0]

def calculate_jaccard_similarity(query_terms, document_terms):
    query_set = set(query_terms.keys())
    doc_set = set(document_terms.keys())
    intersection = len(query_set.intersection(doc_set))
    union = len(query_set.union(doc_set))
    return intersection / union if union != 0 else 0

def search(query, method='cosine'):
    query_terms = query.lower().split()
    query_vector = defaultdict(float)
    for term in query_terms:
        query_vector[term] += 1
    
    results = []
    for url, doc_vector in tfidf_index.items():
        similarity = calculate_cosine_similarity(query_vector, doc_vector) if method == 'cosine' else calculate_jaccard_similarity(query_vector, doc_vector)
        doc_data = next((doc for doc in crawled_data if doc['url'] == url), None)
        if doc_data and similarity > 0:
            # Get tags from index instead of extracting
            tags = tags_index.get(url, ['Artikel'])
            
            results.append({
                'url': url,
                'title': doc_data.get('title', ''),
                'content': doc_data.get('content', '')[:200] + '...',  # Preview
                'score': similarity,
                'date': doc_data.get('date', 'N/A'),
                'image_url': doc_data.get('image_url', ''),
                'tags': tags
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    articles_data = prepare_article_data(crawled_data, page=page)
    return render_template('index.html', **articles_data)

@app.route('/search')
def search_results():
    query = request.args.get('q', '')
    method = request.args.get('method', 'cosine')
    if not query:
        return render_template('index.html')
    
    results = search(query, method)
    
    # Format scores as percentages and ensure all required fields exist
    for result in results:
        result['score'] = result['score']
        # Ensure image_url exists
        if not result.get('image_url') or result['image_url'] == "URL gambar tidak tersedia":
            result['image_url'] = "https://via.placeholder.com/400x200"
        # Ensure tags exist
        if not result.get('tags'):
            result['tags'] = ['Artikel']
            
    return render_template('result.html', query=query, results=results, method=method)

if __name__ == '__main__':
    app.run(debug=True)