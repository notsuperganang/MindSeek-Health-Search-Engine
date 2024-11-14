import scrapy
import re
import json
import os
from urllib.parse import urljoin  # Tambahkan import untuk menggabungkan URL relatif

class CustomHealthArticleSpider(scrapy.Spider):
    name = "custom_health_article_spider"
    link_count = 0
    max_links = 2000  # Batas maksimum link yang akan di-crawl

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
    output_path = r"F:\semester 5\PI\project akhir pi\search-engine-with-flask\mycrawler\hasil_crawl.json"
    crawled_links_path = r"F:\semester 5\PI\project akhir pi\search-engine-with-flask\mycrawler\spiders\crawled_articles.txt"

    def start_requests(self):
        if os.path.exists(self.crawled_links_path):
            with open(self.crawled_links_path, "r") as file:
                start_urls = [line.strip() for line in file if line.strip()]
            for url in start_urls:
                if re.match(self.allowed_pattern, url):
                    yield scrapy.Request(url, callback=self.parse)
        else:
            self.logger.error(f"File {self.crawled_links_path} tidak ditemukan. Pastikan path file benar dan file ada.")

    def parse(self, response):
        if self.link_count >= self.max_links:
            return

        # Ambil judul artikel
        title = response.css('h3.section-header__content-text-title.section-header__content-text-title--xlarge::text').get()

        # Ambil konten artikel
        content = response.css('#articleContent p::text').getall()
        content_text = ' '.join(content)

        # Cek format tanggal pada <span>
        date_elements = response.xpath('//span[@_ngcontent-halodoc-c1151457246 and not(contains(@class, "article-page_reviewer-label"))]/text()').getall()
        date = None
        date_regex = r"^\d{1,2} (Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember) \d{4}$"
        
        for element in date_elements:
            if re.match(date_regex, element.strip()):
                date = element.strip()
                break
        
        if date is None:
            date = "Tanggal tidak tersedia"

        # Ambil semua gambar dari halaman
        image_urls = response.css('img::attr(src)').getall()

        # Filter hanya gambar yang valid, termasuk .webp
        image_urls = [urljoin(response.url, img_url) for img_url in image_urls if img_url.endswith(('jpg', 'jpeg', 'gif', 'webp'))]

        # Jika ada gambar, ambil yang pertama (atau bisa diubah sesuai kebutuhan)
        image_url = image_urls[0] if image_urls else "URL gambar tidak tersedia"

        if response.url not in visited_links:
            visited_links.add(response.url)

            if re.match(self.allowed_pattern, response.url):
                # Tidak memasukkan doctor_additional_info dalam JSON
                data = {
                    'title': title,
                    'url': response.url,
                    'content': content_text,
                    'date': date,
                    'image_url': image_url
                }

                self.save_to_file(data)
                self.save_crawled_link(response.url)
                self.link_count += 1

        # Ambil link berikutnya
        next_links = response.css('a::attr(href)').getall()
        for link in next_links:
            if any(re.search(pattern, link) for pattern in self.disallowed_patterns):
                continue
            absolute_link = response.urljoin(link)
            if re.match(self.allowed_pattern, absolute_link) and absolute_link not in visited_links:
                yield scrapy.Request(absolute_link, callback=self.parse)

    def save_to_file(self, data):
        if not os.path.exists(self.output_path):
            with open(self.output_path, 'w') as f:
                json.dump([], f)

        with open(self.output_path, 'r') as f:
            existing_data = json.load(f)

        existing_data.append(data)

        with open(self.output_path, 'w') as f:
            json.dump(existing_data, f, indent=4)

    def save_crawled_link(self, url):
        with open(self.crawled_links_path, "a") as file:
            file.write(url + "\n")

    def close(self, reason):
        self.logger.info(f"Spider selesai dengan total link yang di-crawl: {self.link_count}")

visited_links = set()
