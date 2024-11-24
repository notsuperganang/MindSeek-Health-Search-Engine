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
        'DOWNLOAD_DELAY': 0.2,
        'CONCURRENT_REQUESTS': 5,
        'ROBOTSTXT_OBEY': True,
        'LOG_LEVEL': 'INFO'
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
    output_path = r"F:\semester 5\PI\project akhir pi\search-engine-with-flask\mycrawler\data\hasil_crawl.json"
    visited_links = set()

    def __init__(self, *args, **kwargs):
        super(HealthArticleSpider, self).__init__(*args, **kwargs)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        if not os.path.exists(self.output_path):
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)

    def parse(self, response):
        if self.link_count >= self.max_links:
            return

        if response.url in self.visited_links:
            return

        self.visited_links.add(response.url)
        article_data = self.extract_article_data(response)

        if article_data['title'] and article_data['content']:
            word_count = len(article_data['content'].split())

            if word_count >= 200 and not self.is_duplicate_title(article_data['title']):
                self.save_article_data(article_data)
                self.link_count += 1
                self.logger.info(f"Berhasil mengekstrak artikel {self.link_count}: {article_data['title']}")
            else:
                self.logger.info(f"Konten tidak valid atau duplikat: {article_data['title']}")

        for link in response.css('a::attr(href)').getall():
            absolute_link = response.urljoin(link)
            if self.is_valid_link(absolute_link):
                yield scrapy.Request(
                    absolute_link, 
                    callback=self.parse,
                    errback=self.handle_error
                )

    def extract_article_data(self, response):
        title = response.css('h3.section-header__content-text-title.section-header__content-text-title--xlarge::text').get()
        article_content = response.css('div[id="articleContent"]')
        content_parts = [
            ' '.join(paragraph.css('::text').getall()).strip()
            for paragraph in article_content.css('p')
            if paragraph.css('::text').get() and len(paragraph.css('::text').get()) >= 20
        ]
        content_text = ' '.join(content_parts).strip()

        date_elements = response.xpath('//span[@_ngcontent-halodoc-c1151457246 and not(contains(@class, "article-page_reviewer-label"))]/text()').getall()
        date = self.extract_date(date_elements)

        image_urls = [
            urljoin(response.url, img_url)
            for img_url in response.css('img::attr(src)').getall()
            if img_url.endswith(('jpg', 'jpeg', 'gif', 'webp'))
        ]
        image_url = image_urls[0] if image_urls else "URL gambar tidak tersedia"

        return {
            'title': title,
            'url': response.url,
            'content': content_text,
            'date': date,
            'image_url': image_url
        }

    def extract_date(self, date_elements):
        date_regex = r"^\d{1,2} (Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember) \d{4}$"
        for element in date_elements:
            if element and re.match(date_regex, element.strip()):
                return element.strip()
        return "Tanggal tidak tersedia"

    def is_valid_link(self, url):
        if not re.match(self.allowed_pattern, url):
            return False
        if url in self.visited_links:
            return False
        if any(re.search(pattern, url) for pattern in self.disallowed_patterns):
            return False
        return True

    def is_duplicate_title(self, title):
        """Cek apakah judul sudah ada di file JSON"""
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                return any(article['title'] == title for article in articles)
        except Exception as e:
            self.logger.error(f"Error membaca file JSON: {e}")
            return False

    def save_article_data(self, data):
        try:
            with open(self.output_path, 'r+', encoding='utf-8') as f:
                articles = json.load(f)
                articles.append(data)
                f.seek(0)
                json.dump(articles, f, indent=4, ensure_ascii=False)
                f.truncate()
        except Exception as e:
            self.logger.error(f"Error saat menyimpan data: {e}")

    def handle_error(self, failure):
        self.logger.error(f"Request gagal: {failure.request.url}")
        self.logger.error(f"Error: {str(failure.value)}")

    def closed(self, reason):
        self.logger.info(f"Spider selesai dengan alasan: {reason}")
        self.logger.info(f"Total artikel yang berhasil di-crawl: {self.link_count}")
