import json

def analyze_crawl_results(json_file_path):
    # Baca file JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Inisialisasi counter
    total_articles = len(articles)
    empty_content = []
    no_date = []
    
    # Analisis setiap artikel
    for article in articles:
        # Cek konten kosong
        if not article['content'].strip():
            empty_content.append({
                'title': article['title'],
                'url': article['url']
            })
            
        # Cek tanggal tidak tersedia
        if article['date'] == "Tanggal tidak tersedia":
            no_date.append({
                'title': article['title'],
                'url': article['url']
            })
    
    # Cetak hasil analisis
    print(f"\nTotal artikel: {total_articles}")
    print(f"\nArtikel dengan konten kosong: {len(empty_content)} ({(len(empty_content)/total_articles)*100:.2f}%)")
    if empty_content:
        print("\nDaftar artikel dengan konten kosong:")
        for idx, article in enumerate(empty_content, 1):
            print(f"{idx}. {article['title']}")
            print(f"   URL: {article['url']}")
    
    print(f"\nArtikel tanpa tanggal: {len(no_date)} ({(len(no_date)/total_articles)*100:.2f}%)")
    if no_date:
        print("\nDaftar artikel tanpa tanggal:")
        for idx, article in enumerate(no_date, 1):
            print(f"{idx}. {article['title']}")
            print(f"   URL: {article['url']}")

# Jalankan analisis
analyze_crawl_results("/home/notsuperganang/Documents/Kuliah/Semester 5/PI/MK/project-UAS/search-engine-with-flask/mycrawler/data/hasil_crawl.json")