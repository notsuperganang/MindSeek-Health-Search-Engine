import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime

# Download NLTK resources
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

def clean_text(text):
    # Lowercase the text
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    return text

def extract_tags(content, num_tags=3):
    if not content or len(content.split()) < 5:
        return ['Artikel']
        
    try:
        stop_words = set(stopwords.words('indonesian') + stopwords.words('english'))
    except:
        stop_words = set()
    
    additional_stops = {
        'halodoc', 'artikel', 'baca', 'juga', 'dapat', 'cara', 'ada', 'bisa',
        'saat', 'anda', 'kamu', 'ini', 'itu', 'nya', 'yah', 'ya', 'jika', 'ke',
        'di', 'dari', 'pada', 'dalam', 'untuk', 'dengan', 'dan', 'atau', 'ini',
        'itu', 'juga', 'sudah', 'saya', 'anda', 'dia', 'mereka', 'kita', 'akan',
        'bisa', 'ada', 'tidak', 'saat', 'oleh', 'setelah', 'para', 'dapat', 'lain',
        'hal', 'orang', 'waktu', 'tahun', 'cara', 'yakni', 'harus', 'selama',
        'jakarta', 'com', 'www', 'html'
    }
    stop_words.update(additional_stops)
    
    cleaned_text = clean_text(content)
    
    try:
        tokens = nltk.word_tokenize(cleaned_text, language='indonesian')
    except:
        tokens = cleaned_text.split()
    
    filtered_tokens = [token for token in tokens 
                      if token not in stop_words 
                      and len(token) > 3]
    
    document = ' '.join(filtered_tokens)
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=50,
        stop_words=list(stop_words)
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform([document])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        term_scores = [(term, score) 
                      for term, score in zip(feature_names, tfidf_scores)
                      if score > 0]
        term_scores.sort(key=lambda x: x[1], reverse=True)
        
        tags = []
        for term, _ in term_scores[:num_tags]:
            tag = ' '.join(word.capitalize() for word in term.split())
            tags.append(tag)
        
        return tags if tags else ['Artikel']
        
    except Exception as e:
        print(f"Error extracting tags: {e}")
        return ['Artikel']

def create_tags_index():
    # Load crawled data
    with open('data/hasil_crawl.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Create tags index
    tags_index = {}
    total = len(articles)
    
    print(f"Processing {total} articles...")
    
    for i, article in enumerate(articles, 1):
        url = article['url']
        content = article['content']
        
        # Extract tags
        tags = extract_tags(content)
        tags_index[url] = tags
        
        # Show progress
        if i % 10 == 0:
            print(f"Processed {i}/{total} articles...")
    
    # Save tags index
    with open('output_indices/tags_index.json', 'w', encoding='utf-8') as f:
        json.dump(tags_index, f, ensure_ascii=False, indent=2)
    
    print("Tags index has been created and saved!")

if __name__ == "__main__":
    create_tags_index()