import scrapy
import re

class HealthArticleSpider(scrapy.Spider):
    name = "health_article_spider"
    start_urls = ["https://www.halodoc.com/kesehatan/kesehatan-mental"]  # URL awal untuk crawling
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

    # Path absolut untuk menyimpan file
    output_file = r"F:\semester 5\PI\project akhir pi\search-engine-with-flask\mycrawler\spiders\crawled_articles.txt"

    def parse(self, response):
        # Cek apakah jumlah link yang telah di-crawl mencapai batas
        if self.link_count >= self.max_links:
            return

        # Menyimpan URL halaman artikel yang di-crawl ke file txt

        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(response.url + "\n")
            self.log(f"URL disimpan: {response.url}")
        except Exception as e:
            self.log(f"Error menulis ke file: {e}")

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
                    if self.link_count < self.max_links:
                        yield response.follow(absolute_link, callback=self.parse)
