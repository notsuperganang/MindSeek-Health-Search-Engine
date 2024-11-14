import scrapy
import re

class HealthArticleSpider(scrapy.Spider):
    name = "health_article_spider"
    start_urls = [
        "https://www.halodoc.com/kesehatan/makanan-dan-nutrisi-anak",
        "https://www.halodoc.com/kesehatan/depresi",
        "https://www.halodoc.com/kesehatan/diabetes",
        "https://www.halodoc.com/kesehatan/olahraga"
    ]
    link_count = 0
    max_links_per_url = 10  # Batas maksimum link untuk setiap URL awal
    current_index = 0  # Indeks URL awal yang sedang diproses
    
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

    def start_requests(self):
        # Memulai dengan URL pertama di start_urls
        yield scrapy.Request(url=self.start_urls[self.current_index], callback=self.parse)

    def parse(self, response):
        # Cek apakah jumlah link yang telah di-crawl untuk URL saat ini mencapai batas
        if self.link_count >= self.max_links_per_url:
            # Reset hitungan link dan lanjut ke URL berikutnya jika ada
            self.link_count = 0
            self.current_index += 1
            if self.current_index < len(self.start_urls):
                # Pindah ke URL berikutnya
                next_url = self.start_urls[self.current_index]
                yield scrapy.Request(url=next_url, callback=self.parse)
            return

        # Menyimpan URL halaman artikel yang di-crawl ke file txt
        with open("crawled_articles1.txt", "a") as f:
            f.write(response.url + "\n")

        # Tambah hitungan link yang telah di-crawl
        self.link_count += 1

        # Mengambil semua link di halaman saat ini dan hanya mengikuti link yang cocok dengan pola artikel
        for link in response.css("a::attr(href)").getall():
            # Membuat link absolut
            absolute_link = response.urljoin(link)

            # Filter hanya URL yang sesuai dengan pola artikel dan tidak termasuk dalam pola yang dilarang
            if re.match(self.allowed_pattern, absolute_link):
                # Mengecek apakah link tidak cocok dengan pola yang dilarang
                if not any(re.search(pattern, absolute_link) for pattern in self.disallowed_patterns):
                    if self.link_count < self.max_links_per_url:
                        yield response.follow(absolute_link, callback=self.parse)
