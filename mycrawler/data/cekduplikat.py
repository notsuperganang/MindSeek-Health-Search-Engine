import json

# Lokasi file JSON
file_path = r"F:\semester 5\PI\project akhir pi\search-engine-with-flask\mycrawler\data\hasil_crawl.json"

# Baca file JSON
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Tampilkan jumlah data total
total_data = len(data)
print(f"Jumlah total data yang dicek: {total_data}")

# Fungsi untuk mendeteksi duplikat berdasarkan title
def find_duplicates(data):
    seen = set()
    duplicates = []

    for item in data:
        title = item.get("title", "").strip()  # Ambil title dan hilangkan spasi berlebih
        if title in seen:
            duplicates.append(item)
        else:
            seen.add(title)
    
    return duplicates

# Panggil fungsi untuk mendeteksi duplikat
duplicates = find_duplicates(data)

# Simpan hasilnya ke file baru
output_path = r"F:\semester 5\PI\project akhir pi\search-engine-with-flask\mycrawler\data\duplicates.json"
with open(output_path, "w", encoding="utf-8") as output_file:
    json.dump(duplicates, output_file, ensure_ascii=False, indent=4)

# Tampilkan jumlah duplikat yang ditemukan
print(f"Jumlah duplikat yang ditemukan: {len(duplicates)}")
print(f"Hasil duplikat telah disimpan di '{output_path}'")
