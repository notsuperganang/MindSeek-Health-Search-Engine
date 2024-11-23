import scrapy
import re
import json
import os
from urllib.parse import urljoin

class HealthArticleSpider(scrapy.Spider):
    name = "full_health_article_spider"
    start_urls = ["https://www.halodoc.com/kesehatan/kesehatan-mental"]
    link_count = 0
    max_links = 2000

    # Konfigurasi crawler
    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,  # Delay antar request
        'CONCURRENT_REQUESTS': 5,  # Jumlah request parallel
        'ROBOTSTXT_OBEY': True,  # Hormati robots.txt
        'LOG_LEVEL': 'INFO'  # Level logging
    }

    # Pattern URL yang diizinkan dan dilarang
    allowed_pattern = r"^https://www\.halodoc\.com/artikel(/.*)?$"
    disallowed_patterns = [
        r"/obatdansuplemen/",
        r"/obat-konten/",
        r"/not-found",
        r"/validasi/hasiltest/",
        r"/server-error",
        r"/general-error",
        r"/sitemap_cari_doctor9\.xml",
        r"/sitemap_rumah_sakit1\.xml",
        r"/cari-dokter/terdekat/",
        r"/rumah-sakit/terdekat/",
        r"/janji-medis/terdekat/"
    ]

    # Path untuk output
    output_path = "/home/notsuperganang/Documents/Kuliah/Semester 5/PI/MK/project-UAS/search-engine-with-flask/mycrawler/data/hasil_crawl.json"
    visited_links = set()

    def __init__(self, *args, **kwargs):
        super(HealthArticleSpider, self).__init__(*args, **kwargs)
        # Pastikan direktori output ada
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Inisialisasi file JSON dengan array kosong yang valid
        if not os.path.exists(self.output_path):
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        else:
            # Validasi file JSON yang sudah ada
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Mencoba membaca JSON untuk memvalidasi
            except json.JSONDecodeError:
                # Jika file rusak, buat ulang dengan array kosong
                with open(self.output_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False)

    def parse(self, response):
        try:
            # Cek batas maksimum
            if self.link_count >= self.max_links:
                return

            # Cek apakah URL sudah pernah dikunjungi
            if response.url in self.visited_links:
                return

            # Tambahkan URL ke set visited
            self.visited_links.add(response.url)

            # Ekstrak data artikel
            article_data = self.extract_article_data(response)

            # Cek panjang konten dan proses hanya jika memenuhi syarat
            if article_data['title'] and article_data['content']:
                # Hitung jumlah kata
                word_count = len(article_data['content'].split())

                if word_count >= 200:
                    # Simpan data artikel jika memenuhi syarat
                    self.save_article_data(article_data)
                    self.link_count += 1
                    self.logger.info(f"Berhasil mengekstrak artikel {self.link_count}: {article_data['title']}")
                else:
                    self.logger.info(f"Konten terlalu pendek ({word_count} kata), mencari link baru...")

            # Crawl link berikutnya
            for link in response.css('a::attr(href)').getall():
                absolute_link = response.urljoin(link)

                # Filter link yang valid
                if self.is_valid_link(absolute_link):
                    yield scrapy.Request(
                        absolute_link, 
                        callback=self.parse,
                        errback=self.handle_error
                    )

        except Exception as e:
            self.logger.error(f"Error saat memproses {response.url}: {str(e)}")

    def extract_article_data(self, response):
        """Ekstrak data dari halaman artikel"""
        # Ekstrak judul
        title = response.css('h3.section-header__content-text-title.section-header__content-text-title--xlarge::text').get()

        # Ekstrak konten dengan selector yang lebih spesifik
        content_parts = []

        # Ambil semua paragraf dari articleContent
        article_content = response.css('div[id="articleContent"]')
        
        # Ekstrak paragraf yang merupakan konten utama
        for paragraph in article_content.css('p'):
            # Skip paragraf kosong atau yang hanya berisi spasi
            text = ' '.join(paragraph.css('::text').getall()).strip()
            if not text:
                continue

            # Skip paragraf yang terlalu pendek
            if len(text) < 20:
                continue

            # Skip paragraf yang mungkin merupakan caption gambar
            if paragraph.css('img'):
                continue

            # Skip paragraf yang berisi link saja
            if paragraph.css('a') and len(paragraph.css('a::text').getall()) == len(text.split()):
                continue

            # Skip paragraf yang mengandung "BACA JUGA"
            if "BACA JUGA" in text.upper():
                continue

            # Skip paragraf yang merupakan judul daftar isi
            if any(title_pattern in text.lower() for title_pattern in [
                "daftar isi",
                "pilihan obat",
                "jenis obat",
                "daftar obat",
                "pilihan",
                "tabel"
            ]):
                continue

            # Skip jika paragraf hanya berisi angka dan karakter khusus
            if re.match(r'^[\d\s\W]+$', text):
                continue

            content_parts.append(text)

        # Gabungkan semua konten valid
        content_text = ' '.join(content_parts)
        content_text = content_text.strip()

        # Log untuk debugging
        if not content_text:
            self.logger.warning(f"Konten kosong untuk URL: {response.url}")
        else:
            word_count = len(content_text.split())
            self.logger.info(f"Berhasil mengekstrak konten dengan {word_count} kata")
        
        # Ekstrak tanggal
        date_elements = response.xpath('//span[@_ngcontent-halodoc-c1151457246 and not(contains(@class, "article-page_reviewer-label"))]/text()').getall()
        date = self.extract_date(date_elements)
        
        # Ekstrak gambar
        image_urls = response.css('img::attr(src)').getall()
        image_url = self.get_first_valid_image(image_urls, response.url)

        # Log debugging info
        self.logger.info(f"Extracted content length: {len(content_text)}")
    
        return {
            'title': title,
            'url': response.url,
            'content': content_text,
            'date': date,
            'image_url': image_url
        }
        content_text = ' '.join(content_parts)
        content_text = content_text.strip()

        # Log untuk debugging
        if not content_text:
            self.logger.warning(f"Konten masih kosong untuk URL: {response.url}")
            # Log semua konten yang ditemukan
            self.logger.info(f"Paragraphs found: {paragraphs}")
            self.logger.info(f"Strong texts found: {strong_texts}")
            self.logger.info(f"List items found: {list_items}")
            self.logger.info(f"Headings found: {headings}")
        
        # Ekstrak tanggal
        date_elements = response.xpath('//span[@_ngcontent-halodoc-c1151457246 and not(contains(@class, "article-page_reviewer-label"))]/text()').getall()
        date = self.extract_date(date_elements)
        
        # Ekstrak gambar
        image_urls = response.css('img::attr(src)').getall()
        image_url = self.get_first_valid_image(image_urls, response.url)

        # Log debugging info
        self.logger.info(f"Extracted content length: {len(content_text)}")
    
        return {
            'title': title,
            'url': response.url,
            'content': content_text,
            'date': date,
            'image_url': image_url
        }

    def extract_date(self, date_elements):
        """Ekstrak tanggal dari elemen yang ditemukan"""
        date_regex = r"^\d{1,2} (Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember) \d{4}$"
        
        for element in date_elements:
            if element and re.match(date_regex, element.strip()):
                return element.strip()
        return "Tanggal tidak tersedia"

    def get_first_valid_image(self, image_urls, base_url):
        """Ambil URL gambar pertama yang valid"""
        valid_images = [
            urljoin(base_url, img_url) 
            for img_url in image_urls 
            if img_url and img_url.endswith(('jpg', 'jpeg', 'png', 'gif', 'webp'))
        ]
        return valid_images[0] if valid_images else "URL gambar tidak tersedia"

    def is_valid_link(self, url):
        """Cek apakah URL valid untuk di-crawl"""
        if not re.match(self.allowed_pattern, url):
            return False
            
        if url in self.visited_links:
            return False
            
        if any(re.search(pattern, url) for pattern in self.disallowed_patterns):
            return False
            
        return True

    def save_article_data(self, data):
        """Simpan data artikel ke file JSON dengan penanganan error yang lebih baik"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Baca data yang sudah ada
                articles = []
                if os.path.exists(self.output_path):
                    with open(self.output_path, 'r', encoding='utf-8') as f:
                        articles = json.load(f)
                
                # Tambahkan artikel baru
                articles.append(data)
                
                # Tulis kembali ke file dengan temporary file untuk mencegah corrupt
                temp_file = f"{self.output_path}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, indent=4, ensure_ascii=False)
                    
                # Rename temporary file ke file asli
                os.replace(temp_file, self.output_path)
                break  # Keluar dari loop jika berhasil
                
            except Exception as e:
                self.logger.error(f"Error saat menyimpan data (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:  # Jika ini percobaan terakhir
                    raise  # Re-raise exception jika semua percobaan gagal
                
    def handle_error(self, failure):
        """Handle error saat crawling"""
        self.logger.error(f"Request gagal: {failure.request.url}")
        self.logger.error(f"Error: {str(failure.value)}")

    def closed(self, reason):
        """Dipanggil saat spider selesai"""
        self.logger.info(f"Spider selesai dengan alasan: {reason}")
        self.logger.info(f"Total artikel yang berhasil di-crawl: {self.link_count}")