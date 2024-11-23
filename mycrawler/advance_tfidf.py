"""
Advanced TF-IDF Implementation with progress tracking and improved error handling
"""

import json
import math
import logging
import gc
from pathlib import Path
from typing import Dict, List, Set, Union, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import numpy as np
from datetime import datetime
from tqdm import tqdm  # Import tqdm for progress bars

# Configure logging dengan level DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'tfidf_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TFIDFConfig:
    """Configuration class for TF-IDF processing parameters"""
    min_df: int = 2  # Minimum document frequency
    max_df: float = 0.85  # Maximum document frequency (as fraction)
    min_word_length: int = 3  # Minimum word length
    normalize: bool = True  # Normalize vectors
    use_idf: bool = True  # Use IDF weighting
    smooth_idf: bool = True  # Smooth IDF weights
    batch_size: int = 100  # Batch size for processing

class DocumentPreprocessor:
    def __init__(self, config: TFIDFConfig):
        self.config = config
        self.stemmer = StemmerFactory().create_stemmer()
        self._load_stop_words()
        logger.debug("DocumentPreprocessor initialized")
        
    def _load_stop_words(self) -> None:
        """Load Indonesian stop words"""
        self.stop_words = {
            "yang", "di", "ke", "dari", "dan", "ini", "itu", "dengan", "untuk", 
            "atau", "pada", "adalah", "dalam", "oleh", "akan", "sebagai", "sangat", 
            "juga", "tidak", "karena", "bagi", "hanya", "kita", "saya", "kamu", 
            "kami", "kalian", "mereka", "beliau", "ada", "akan", "bisa", "bukan",
            "harus", "apakah", "apa", "agar", "tersebut", "demikian", "tetapi",
            "supaya", "sedangkan", "serta", "namun", "antara", "itu", "sebuah",
            "setelah", "sekitar", "selalu", "sejak", "sedang", "masih", "pun",
            "pernah", "maka", "seperti", "sampai", "tanpa", "yaitu", "selain",
            "belum", "perlu", "kapan", "dimana", "bagaimana", "siapa", "dalam",
            "demi", "jika", "jikalau", "manakala", "seusai", "sebelum", "sehabis",
            "ketika", "dimana", "terus", "saja", "atau", "bahwa", "sebab", "lalu", "baik"
        }
        logger.debug("Stop words loaded")
    
    def preprocess_text(self, text: str) -> List[str]:
        try:
            if not isinstance(text, str):
                logger.warning(f"Expected string input, got {type(text)}")
                return []
                
            tokens = text.lower().split()
            processed_tokens = [
                self.stemmer.stem(word) 
                for word in tokens 
                if (word not in self.stop_words and 
                    len(word) >= self.config.min_word_length)
            ]
            return processed_tokens
        except Exception as e:
            logger.error(f"Error in text preprocessing: {str(e)}")
            return []

class TFIDFProcessor:
    def __init__(self, config: TFIDFConfig):
        self.config = config
        self.preprocessor = DocumentPreprocessor(config)
        self.reset_indices()
        logger.debug("TFIDFProcessor initialized")
    
    def reset_indices(self) -> None:
        self.inverted_index = defaultdict(set)
        self.tfidf_index = defaultdict(dict)
        self.df = Counter()
        self.vocabulary = {}
        self.document_count = 0
        logger.debug("Indices reset")
    
    def _check_df_threshold(self, term: str, total_docs: int) -> bool:
        """Check if term meets document frequency thresholds"""
        if self.df[term] < self.config.min_df:
            return False
        if (self.df[term] / total_docs) > self.config.max_df:
            return False
        return True
    
    def _compute_idf(self, term: str) -> float:
        """Compute IDF for a term"""
        if not self.config.use_idf:
            return 1.0

        n_samples = self.document_count
        df = self.df[term]

        if self.config.smooth_idf:
            n_samples += 1
            df += 1

        return math.log(n_samples / df) + 1 if df else 0

    def _process_batch(self, batch: List[Dict], is_first_pass: bool) -> None:
        """Process a batch of documents"""
        for doc in batch:
            try:
                doc_id = doc['url']
                content = doc.get('content', '')
                
                if not content:
                    logger.warning(f"Empty content for document {doc_id}")
                    continue
                
                terms = self.preprocessor.preprocess_text(content)
                
                if is_first_pass:
                    # First pass: build document frequencies
                    for term in set(terms):
                        self.df[term] += 1
                        self.inverted_index[term].add(doc_id)
                else:
                    # Second pass: compute TF-IDF
                    term_counts = Counter(terms)
                    doc_length = len(terms)
                    
                    if doc_length == 0:
                        logger.warning(f"No valid terms found in document {doc_id}")
                        continue
                    
                    doc_tfidf = {}
                    for term, count in term_counts.items():
                        if term in self.vocabulary:
                            tf = count / doc_length
                            idf = self._compute_idf(term)
                            doc_tfidf[term] = tf * idf
                    
                    if self.config.normalize and doc_tfidf:
                        norm = math.sqrt(sum(score * score for score in doc_tfidf.values()))
                        if norm > 0:
                            doc_tfidf = {term: score/norm for term, score in doc_tfidf.items()}
                    
                    self.tfidf_index[doc_id] = doc_tfidf
                    
            except Exception as e:
                logger.error(f"Error processing document {doc.get('url', 'unknown')}: {str(e)}")
                continue

    def process_documents(self, documents: List[Dict]) -> None:
        try:
            total_docs = len(documents)
            logger.info(f"Starting document processing for {total_docs} documents")
            self.reset_indices()
            self.document_count = total_docs
            
            # Process in batches
            batch_size = self.config.batch_size
            
            # First pass: Build document frequencies
            logger.info("Starting first pass - building document frequencies")
            for i in tqdm(range(0, total_docs, batch_size), desc="First pass"):
                batch = documents[i:i + batch_size]
                self._process_batch(batch, is_first_pass=True)
                gc.collect()  # Force garbage collection
            
            # Build vocabulary
            logger.info("Building vocabulary")
            self.vocabulary = {
                term: idx for idx, term in enumerate(
                    sorted(term for term in self.df 
                          if self._check_df_threshold(term, total_docs))
                )
            }
            logger.info(f"Vocabulary size: {len(self.vocabulary)}")
            
            # Second pass: Compute TF-IDF scores
            logger.info("Starting second pass - computing TF-IDF scores")
            for i in tqdm(range(0, total_docs, batch_size), desc="Second pass"):
                batch = documents[i:i + batch_size]
                self._process_batch(batch, is_first_pass=False)
                gc.collect()
            
            logger.info("Document processing completed")
            
        except Exception as e:
            logger.error(f"Error in document processing: {str(e)}")
            raise
    def save_indices(self, output_dir: Union[str, Path]) -> None:
        """
        Save indices to JSON files
        
        Args:
            output_dir: Directory to save the index files
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare inverted index for serialization
            inverted_dict = {
                term: list(docs) 
                for term, docs in self.inverted_index.items()
                if term in self.vocabulary
            }
            
            # Save files
            with open(output_dir / 'inverted_index.json', 'w', encoding='utf-8') as f:
                json.dump(inverted_dict, f, ensure_ascii=False, indent=4)
                
            with open(output_dir / 'tfidf_index.json', 'w', encoding='utf-8') as f:
                json.dump(dict(self.tfidf_index), f, ensure_ascii=False, indent=4)
                
            with open(output_dir / 'vocabulary.json', 'w', encoding='utf-8') as f:
                json.dump(self.vocabulary, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Successfully saved indices to {output_dir}")
            
        except Exception as e:
            logger.error(f"Error saving indices: {str(e)}")
            raise

def main():
    try:
        logger.info("Starting TF-IDF processing")
        
        # Load data
        file_path = r'data/hasil_crawl.json'
        logger.info(f"Loading data from {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        logger.info(f"Loaded {len(data)} documents")
        
        # Initialize processor with config
        config = TFIDFConfig(
            min_df=2,
            max_df=0.85,
            min_word_length=3,
            normalize=True,
            use_idf=True,
            smooth_idf=True,
            batch_size=100  # Process 100 documents at a time
        )
        
        processor = TFIDFProcessor(config)
        
        # Process documents
        processor.process_documents(data)
        
        # Save indices
        output_dir = 'output_indices'
        logger.info(f"Saving indices to {output_dir}")
        processor.save_indices(output_dir)
        
        logger.info("Processing completed successfully")
        
    except FileNotFoundError:
        logger.error(f"Could not find file: {file_path}")
    except json.JSONDecodeError:
        logger.error("Error decoding JSON file")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()