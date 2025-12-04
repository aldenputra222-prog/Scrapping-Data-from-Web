# 🏫 Indonesia School Data Scraper (DAPO)

Project ini adalah alat **Data Engineering** berbasis Python untuk mengumpulkan data detail sekolah (SD, SMP, SMA, SMK) secara otomatis dari portal publik Data Pokok Pendidikan (DAPO) Kemendikdasmen.

Script ini dirancang untuk ketahanan (robustness) terhadap koneksi yang tidak stabil dan mampu menangani ribuan data.

## 🚀 Fitur Utama

- **Smart Filtering:** Mencari sekolah berdasarkan keyword kota (Contoh: Bandung, Yogyakarta, Bogor, Surabaya, Malang, Sidoarjo).
- **Deep Extraction:** Mengambil data detail hingga ke fasilitas (jumlah ruang kelas, lab), data guru (PTK), dan koordinat lokasi.
- **Resume Capability:** Jika script berhenti di tengah jalan, script akan melanjutkan dari data terakhir (tidak mulai dari nol).
- **Anti-Failure:** Dilengkapi dengan *Retry Logic* otomatis jika server target *down* atau memblokir sementara.
- **Clean Output:** Hasil langsung dalam format `.csv` yang terstruktur dan siap untuk analisis (DuckDB/Pandas).

## 🛠️ Teknologi yang Digunakan

- **Python 3.x**
- **Requests & Urllib3:** Untuk manajemen HTTP request dan session.
- **BeautifulSoup4 (bs4):** Untuk parsing HTML profil sekolah.
- **CSV Module:** Penyimpanan data terstruktur.

## 📋 Struktur Data Output

Dataset yang dihasilkan mencakup kolom-kolom vital untuk analisis pendidikan:
- **Identitas:** Nama Sekolah, NPSN, Status (Negeri/Swasta), Akreditasi.
- **Lokasi:** Provinsi, Kota, Kecamatan, Alamat, Koordinat (Lat/Long).
- **Statistik:** Jumlah Siswa (L/P), Guru, Tenaga Pendidik.
- **Fasilitas:** Ruang Kelas, Perpustakaan, Laboratorium, Listrik, Internet.

## ⚙️ Cara Menjalankan

1. **Clone repository ini**
   ```bash
   git clone [https://github.com/username-kamu/dapo-school-scraper.git](https://github.com/username-kamu/dapo-school-scraper.git)

2. **Install dependencies**
   ```bash
   pip install requests beautifulsoup4

3. **Jalankan Script**
   ```bash
   python main_scraper.py

4. Hasil Data akan tersimpan otomatis di folder result/data_sekolah_combined.csv.

⚠️ Disclaimer
Project ini dibuat untuk tujuan edukasi dan analisis data publik. Harap gunakan dengan bijak dan jangan membebani server pemerintah dengan request yang berlebihan (script ini sudah dilengkapi delay/backoff).

⚠️ Disclaimer

Project ini dibuat semata-mata untuk **Tujuan Edukasi dan Pembelajaran** (Educational Purposes Only) mengenai teknik Data Engineering dan Web Scraping.

1. **Sumber Data:** Data yang diambil bersumber dari portal publik yang dapat diakses secara terbuka oleh siapa saja tanpa memerlukan kredensial khusus.
2. **Tidak Ada Data Pribadi:** Script ini tidak mengambil data sensitif (PII) seperti NIK siswa, nomor telepon, atau data pribadi lainnya. Hanya data statistik sekolah umum.
3. **Penggunaan Wajar:** Script dilengkapi dengan delay/sleep untuk mencegah pembebanan berlebih pada server target.
4. **Tanggung Jawab:** Penggunaan script ini menjadi tanggung jawab pengguna sepenuhnya. Pembuat tidak bertanggung jawab atas penyalahgunaan data.
