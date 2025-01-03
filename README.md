<h1 align="center">🔍 MindSeek</h1>
<h2 align="center">Health Information Search Engine with Advanced Text Similarity</h2>

<p align="center">
  <img src="mycrawler/static/img/logo.jpg" alt="MindSeek Search Engine Banner"/>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.5%2B-orange.svg)](https://scrapy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A sophisticated search engine system that crawls, indexes, and retrieves health-related articles using advanced text similarity algorithms and natural language processing techniques.

## 🚀 Features

- **Advanced Search Capabilities**
  - Cosine Similarity-based search
  - Jaccard Similarity matching
  - Tag-based article categorization
  - Real-time search suggestions

- **Powerful Web Crawling**
  - Custom Scrapy spiders
  - Duplicate content detection
  - Structured data extraction
  - Automated tag generation

- **Smart Text Processing**
  - TF-IDF vectorization
  - Inverted index creation
  - Natural language preprocessing
  - Tag extraction and indexing

- **Modern Web Interface**
  - Responsive design
  - Interactive particle background
  - Dynamic search results
  - Article preview cards

## 📋 Requirements

```txt
flask>=2.0.0
scrapy>=2.5.0
numpy>=1.19.0
scikit-learn>=0.24.0
nltk>=3.6.0
python-dotenv>=0.19.0
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/notsuperganang/MindSeek-Health-Search-Engine.git
cd mindseek
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Running the Crawler

```bash
cd mycrawler
scrapy crawl custom_spider
```

### Starting the Search Engine

```bash
python -m mycrawler.app
```

The application will be available at `http://localhost:5000`

## 🏗️ Project Structure

```
mindseek/
├── mycrawler/
│   ├── spiders/
│   │   ├── custom_spider.py    # Main crawler implementation
│   │   ├── full_spider.py      # Complete site crawler
│   │   └── limited_spider.py   # Restricted crawler
│   ├── data/                   # Crawled data storage
│   ├── output_indices/         # Search indices
│   ├── static/                 # Frontend assets
│   ├── templates/              # HTML templates
│   ├── app.py                  # Flask application
│   └── search.py              # Search implementation
├── requirements.txt
└── scrapy.cfg
```

## 🔧 Technical Implementation

### Search Algorithms
- **Cosine Similarity**: Measures document similarity using TF-IDF vectors
- **Jaccard Similarity**: Computes similarity based on term overlap
- **Inverted Index**: Optimizes search performance

### Data Processing Pipeline
1. Web Crawling (Scrapy)
2. Content Extraction
3. Tag Generation
4. Text Preprocessing
5. Index Creation
6. Search Implementation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask documentation and community
- Scrapy development team
- NLTK and scikit-learn communities

## 📬 Contact

Your Name - [@notsuperganang](https://www.instagram.com/notsuperganang/) - ganangsetyohadi@gmail.com

Project Link: [https://github.com/notsuperganang/MindSeek-Health-Search-Engine.git](https://github.com/notsuperganang/MindSeek-Health-Search-Engine.git)

---
<p align="center">
  Made with ❤️ for better health information access
</p>