import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
import re
import string
from collections import Counter
from datetime import datetime
import pickle
import logging
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import nltk
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

@dataclass
class ProcessedArticle:
    id: int
    title: str
    url: str
    content: str
    processed_content: str
    date: str
    top_terms: List[Tuple[str, float]]
    named_entities: List[str]
    keywords: List[str]

class AdvancedTextProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize with configurable parameters
        """
        self.config = {
            'min_word_length': 3,
            'max_word_length': 30,
            'min_df': 2,
            'max_df': 0.95,
            'ngram_range': (1, 3),
            'num_topics': 10,
            'num_clusters': 8,
            'num_keywords': 10
        }
        if config:
            self.config.update(config)

        # Initialize processors
        self.stemmer = StemmerFactory().create_stemmer()
        self.stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
        
        # Setup logging
        self.setup_logging()
        
        # Additional stopwords
        self.custom_stopwords = set([
            "yang", "di", "ke", "dari", "dan", "ini", "itu", "dengan", "untuk", "atau", "pada", "adalah",
            "dalam", "oleh", "akan", "sebagai", "sangat", "juga", "tidak", "karena", "bagi", "hanya", "kita",
            "saya", "kamu", "kami", "kalian", "mereka", "beliau", "ada", "akan", "bisa", "bukan", "harus",
            "apakah", "apa", "agar", "tersebut", "demikian", "tetapi", "supaya", "sedangkan", "serta", "namun",
            "antara", "itu", "sebuah", "setelah", "sekitar", "selalu", "sejak", "sedang", "masih", "pun",
            "pernah", "maka", "seperti", "sampai", "tanpa", "yaitu", "selain", "belum", "perlu", "kapan",
            "dimana", "bagaimana", "siapa", "dalam", "demi", "jika", "jikalau", "manakala", "seusai",
            "sebelum", "sehabis", "ketika", "dimana", "terus", "saja", "atau", "bahwa", "sebab", "lalu", "baik"
            ])
        
        # Compile regex patterns
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
        self.number_pattern = re.compile(r'\d+')

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('text_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def clean_text(self, text: str) -> str:
        """
        Advanced text cleaning with multiple steps
        """
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove URLs
            text = self.url_pattern.sub('', text)
            
            # Remove email addresses
            text = self.email_pattern.sub('', text)
            
            # Remove numbers but keep years
            text = self.number_pattern.sub(
                lambda m: m.group() if len(m.group()) == 4 and 1900 <= int(m.group()) <= 2100 else ' ',
                text
            )
            
            # Remove punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Remove words that are too short or too long
            text = ' '.join(
                word for word in text.split()
                if self.config['min_word_length'] <= len(word) <= self.config['max_word_length']
            )
            
            return text
        except Exception as e:
            self.logger.error(f"Error in clean_text: {str(e)}")
            return text

    def extract_named_entities(self, text: str) -> List[str]:
        """
        Extract named entities using NLTK
        """
        try:
            sentences = nltk.sent_tokenize(text)
            named_entities = []
            
            for sentence in sentences:
                words = nltk.word_tokenize(sentence)
                tagged = nltk.pos_tag(words)
                
                # Extract proper nouns
                named_entities.extend([word for word, pos in tagged if pos in ['NNP', 'NNPS']])
                
            return list(set(named_entities))
        except Exception as e:
            self.logger.error(f"Error in extract_named_entities: {str(e)}")
            return []

    def process_articles(self, articles: List[Dict]) -> List[ProcessedArticle]:
        """
        Process articles with advanced features
        """
        processed_articles = []
        
        for idx, article in enumerate(articles):
            try:
                # Clean and preprocess text
                cleaned_content = self.clean_text(article['content'])
                processed_content = self.stopword_remover.remove(cleaned_content)
                processed_content = self.stemmer.stem(processed_content)
                
                # Extract named entities
                named_entities = self.extract_named_entities(article['content'])
                
                processed_article = ProcessedArticle(
                    id=idx,
                    title=article['title'],
                    url=article['url'],
                    content=article['content'],
                    processed_content=processed_content,
                    date=article['date'],
                    top_terms=[],  # Will be filled later
                    named_entities=named_entities,
                    keywords=[]  # Will be filled later
                )
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                self.logger.error(f"Error processing article {idx}: {str(e)}")
                continue
                
        return processed_articles

    def create_document_term_matrix(self, processed_articles: List[ProcessedArticle]):
        """
        Create TF-IDF matrix with advanced features
        """
        self.vectorizer = TfidfVectorizer(
            min_df=self.config['min_df'],
            max_df=self.config['max_df'],
            ngram_range=self.config['ngram_range'],
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True  # Apply sublinear scaling to term frequencies
        )
        
        # Create document-term matrix
        self.dtm = self.vectorizer.fit_transform([art.processed_content for art in processed_articles])
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        return self.dtm

    def perform_topic_modeling(self) -> Tuple[Any, List[List[Tuple[str, float]]]]:
        """
        Perform topic modeling using LDA and NMF
        """
        # LDA for topic modeling
        lda = LatentDirichletAllocation(
            n_components=self.config['num_topics'],
            random_state=42,
            learning_method='online'
        )
        lda_output = lda.fit_transform(self.dtm)
        
        # NMF as alternative
        nmf = NMF(
            n_components=self.config['num_topics'],
            random_state=42
        )
        nmf_output = nmf.fit_transform(self.dtm)
        
        # Extract top terms for each topic
        topic_terms = []
        for topic_idx, topic in enumerate(lda.components_):
            top_terms = [
                (self.feature_names[i], score)
                for i, score in sorted(enumerate(topic), key=lambda x: x[1], reverse=True)
            ][:10]
            topic_terms.append(top_terms)
            
        return (lda_output, nmf_output), topic_terms

    def cluster_documents(self):
        """
        Cluster documents using K-means
        """
        kmeans = KMeans(
            n_clusters=self.config['num_clusters'],
            random_state=42
        )
        clusters = kmeans.fit_predict(self.dtm)
        
        return clusters

    def extract_keywords(self, processed_article: ProcessedArticle) -> List[str]:
        """
        Extract keywords using multiple methods
        """
        # TF-IDF based keywords
        tfidf_vector = self.vectorizer.transform([processed_article.processed_content])
        tfidf_scores = zip(self.feature_names, tfidf_vector.toarray()[0])
        tfidf_keywords = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)[:self.config['num_keywords']]
        
        # Add named entities to keywords
        keywords = [term for term, _ in tfidf_keywords]
        keywords.extend(processed_article.named_entities)
        
        return list(set(keywords))

    def analyze_articles(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of articles
        """
        self.logger.info("Starting article analysis")
        
        # Process articles
        processed_articles = self.process_articles(articles)
        
        # Create document-term matrix
        dtm = self.create_document_term_matrix(processed_articles)
        
        # Perform topic modeling
        topic_models, topic_terms = self.perform_topic_modeling()
        
        # Cluster documents
        clusters = self.cluster_documents()
        
        # Calculate document similarities
        similarity_matrix = cosine_similarity(dtm)
        
        # Extract keywords for each article
        for article in processed_articles:
            article.keywords = self.extract_keywords(article)
            
        # Prepare results
        analysis_results = {
            'processed_articles': processed_articles,
            'document_term_matrix': dtm,
            'topic_models': topic_models,
            'topic_terms': topic_terms,
            'clusters': clusters,
            'similarity_matrix': similarity_matrix,
            'vectorizer': self.vectorizer,
            'feature_names': self.feature_names
        }
        
        self.logger.info("Article analysis completed")
        return analysis_results

    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        Save analysis results
        """
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(results, f)
            self.logger.info(f"Results saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")

# Contoh penggunaan
if __name__ == "__main__":
    # Load articles
    with open('hasil_crawl.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Initialize processor with custom config
    config = {
        'min_word_length': 3,
        'max_word_length': 30,
        'min_df': 2,
        'max_df': 0.95,
        'ngram_range': (1, 3),
        'num_topics': 10,
        'num_clusters': 8,
        'num_keywords': 10
    }
    
    processor = AdvancedTextProcessor(config)
    
    # Analyze articles
    results = processor.analyze_articles(articles)
    
    # Save results
    processor.save_results(results, 'analysis_results.pkl')
    
    # Print some example results
    print("\nSample Topic Terms:")
    for idx, terms in enumerate(results['topic_terms'][:3]):
        print(f"\nTopic {idx + 1}:")
        for term, score in terms[:5]:
            print(f"- {term}: {score:.4f}")
    
    print("\nSample Article Keywords:")
    for article in results['processed_articles'][:3]:
        print(f"\nArticle: {article.title}")
        print("Keywords:", ', '.join(article.keywords[:5]))