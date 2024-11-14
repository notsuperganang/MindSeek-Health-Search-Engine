import scrapy
import re
import json
import os

class CustomHealthArticleSpider(scrapy.Spider):
    name = "custom_health_article_spider"
    link_count = 0
    max_links = 10  # Batas maksimum link yang akan di-crawl

    # Regex untuk menyaring URL berdasarkan robots.txt dan hanya mengikuti yang tidak dilarang
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

    # Path output untuk menyimpan hasil dalam JSON
    output_path = r"D:\__mata kuliah\Penelusuran Informasi\UAS\search-engine-with-flask\mycrawler\spiders\hasil_crawl1.json"

    def start_requests(self):
        file_path = r"D:\__mata kuliah\Penelusuran Informasi\UAS\search-engine-with-flask\mycrawler\spiders\crawled_articles1.txt"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                start_urls = [line.strip() for line in file if line.strip()]
            for url in start_urls:
                if re.match(self.allowed_pattern, url):
                    yield scrapy.Request(url, callback=self.parse)
        else:
            self.logger.error(f"File {file_path} tidak ditemukan. Pastikan path file benar dan file ada.")

    def parse(self, response):
        if self.link_count >= self.max_links:
            return
        
        # Ambil judul artikel dari tag <h3> dengan class tertentu
        title = response.xpath('//h3[@class="section-header__content-text-title section-header__content-text-title--xlarge"]/text()').get()
        
        # Ambil konten dari <div> dengan id 'articleContent' dan class 'article__content ql-editor'
        content = response.xpath('//div[@id="articleContent" and contains(@class, "article__content ql-editor")]/p/text()').getall()
        content_text = ' '.join(content)

        if re.match(self.allowed_pattern, response.url):
            # Data yang akan disimpan
            data = {
                'title': title,
                'url': response.url,
                'content': content_text,
            }

            # Tambahkan data ke file JSON
            self.save_to_file(data)
            self.link_count += 1

        # Mengambil link berikutnya
        next_links = response.xpath('//a/@href').getall()
        for link in next_links:
            if any(re.search(pattern, link) for pattern in self.disallowed_patterns):
                continue
            absolute_link = response.urljoin(link)
            if re.match(self.allowed_pattern, absolute_link):
                yield scrapy.Request(absolute_link, callback=self.parse)

    def save_to_file(self, data):
        # Cek apakah file sudah ada
        if not os.path.exists(self.output_path):
            # Jika belum ada, buat file baru dengan array JSON kosong
            with open(self.output_path, 'w') as f:
                json.dump([], f)

        # Baca isi file JSON
        with open(self.output_path, 'r') as f:
            existing_data = json.load(f)

        # Tambahkan data baru
        existing_data.append(data)

        # Tulis kembali data ke file JSON
        with open(self.output_path, 'w') as f:
            json.dump(existing_data, f, indent=4)

    def close(self, reason):
        self.logger.info(f"Spider selesai dengan total link yang di-crawl: {self.link_count}")
