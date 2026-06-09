# ETL Pipeline — Fashion Studio

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![ETL](https://img.shields.io/badge/Pipeline-ETL-success)
![Testing](https://img.shields.io/badge/Testing-Pytest-yellow)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)
![Data](https://img.shields.io/badge/Output-CSV%20%7C%20Google%20Sheets-lightgrey)

Proyek ini adalah pipeline **ETL (Extract, Transform, Load)** untuk mengambil data produk dari website **Fashion Studio Dicoding**, membersihkan data mentah, mengubah struktur data menjadi format siap pakai, lalu menyimpan hasil akhir ke **CSV** dan **Google Sheets**.

Pipeline ini dibuat secara modular agar setiap proses mudah diuji, diperbaiki, dan dikembangkan.

---

## Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Fitur Utama](#fitur-utama)
- [Arsitektur Pipeline](#arsitektur-pipeline)
- [Struktur Project](#struktur-project)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Konfigurasi Environment](#konfigurasi-environment)
- [Instalasi Project](#instalasi-project)
- [Cara Menjalankan Pipeline](#cara-menjalankan-pipeline)
- [Output Data](#output-data)
- [Proses Extract](#proses-extract)
- [Proses Transform](#proses-transform)
- [Proses Load](#proses-load)
- [Pengujian Unit Test](#pengujian-unit-test)
- [Coverage Test](#coverage-test)
- [Keamanan Credential](#keamanan-credential)
- [Troubleshooting](#troubleshooting)
- [Ringkasan Project](#ringkasan-project)

---

## Gambaran Umum

Pipeline ini menjalankan tiga tahap utama.

Pertama, sistem mengambil data produk dari halaman website Fashion Studio Dicoding. Kedua, sistem membersihkan data mentah agar hanya data valid yang digunakan. Ketiga, sistem menyimpan hasil akhir ke file CSV dan Google Sheets.

Data yang diproses mencakup nama produk, harga, rating, jumlah warna, ukuran, kategori gender, dan waktu pengambilan data.

---

## Fitur Utama

- Scraping data produk dari beberapa halaman website.
- Generator URL otomatis untuk halaman pertama hingga halaman terakhir.
- Parsing HTML menggunakan BeautifulSoup.
- Retry mechanism untuk menangani timeout dan gangguan koneksi.
- Error handling untuk timeout, connection error, HTTP error, dan data kosong.
- Pembersihan data produk tidak valid.
- Konversi harga dari USD ke IDR.
- Ekstraksi nilai numerik dari rating dan jumlah warna.
- Penghapusan data duplikat.
- Penyimpanan data bersih ke file CSV.
- Integrasi dengan Google Sheets API.
- Unit test untuk `config.py`, `main.py`, `extract.py`, `transform.py`, dan `load.py`.
- Coverage test dengan target 100% untuk kode utama.

---

## Arsitektur Pipeline

```text
Website Fashion Studio Dicoding
            |
            v
+----------------------+
| Extract              |
| - Generate URL       |
| - Request halaman    |
| - Parse HTML         |
| - Ambil data produk  |
+----------------------+
            |
            v
+----------------------+
| Transform            |
| - Validasi kolom     |
| - Bersihkan title    |
| - Konversi harga     |
| - Bersihkan rating   |
| - Bersihkan colors   |
| - Bersihkan size     |
| - Bersihkan gender   |
| - Hapus duplikasi    |
+----------------------+
            |
            v
+----------------------+
| Load                 |
| - Simpan ke CSV      |
| - Upload ke Sheets   |
+----------------------+
```

---

## Struktur Project

```text
BFPD/
├── .coveragerc
├── .env
├── .gitignore
├── README.md
├── config.py
├── main.py
├── requirements.txt
├── dicoding-fashion-products.csv
│
├── utils/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
└── tests/
    ├── test_config.py
    ├── test_main.py
    ├── test_extract.py
    ├── test_transform.py
    └── test_load.py
```

Keterangan folder dan file:

| Path | Fungsi |
|---|---|
| `main.py` | Entry point untuk menjalankan seluruh pipeline ETL. |
| `config.py` | Mengambil dan memvalidasi konfigurasi dari environment variable. |
| `utils/extract.py` | Mengambil dan melakukan parsing data produk dari website. |
| `utils/transform.py` | Membersihkan, memvalidasi, dan mengubah data mentah menjadi data siap pakai. |
| `utils/load.py` | Menyimpan data ke CSV dan Google Sheets. |
| `tests/` | Berisi unit test untuk setiap modul utama. |
| `.coveragerc` | Konfigurasi coverage agar hanya menghitung kode utama. |
| `.env` | Berisi konfigurasi lokal dan credential path. |
| `requirements.txt` | Daftar dependency Python. |

---

## Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Bahasa utama project. |
| Requests | Mengirim HTTP request ke website sumber. |
| BeautifulSoup4 | Parsing dan ekstraksi data dari HTML. |
| Pandas | Transformasi dan pengolahan data tabular. |
| python-dotenv | Membaca environment variable dari file `.env`. |
| Google API Python Client | Integrasi data ke Google Sheets. |
| Google Auth | Autentikasi service account Google. |
| Pytest | Unit testing. |
| Coverage.py | Mengukur cakupan pengujian kode. |

---

## Konfigurasi Environment

Buat file `.env` di root project.

Contoh isi file `.env`:

```env
SPREADSHEET_ID=your_google_spreadsheet_id
SERVICE_ACCOUNT_FILE=./your_service_account_file.json
OUTPUT_CSV=dicoding-fashion-products.csv
TOTAL_PAGES=50
EXCHANGE_RATE=16000
SHEET_NAME=Sheet1
```

Keterangan konfigurasi:

| Variable | Wajib | Default | Deskripsi |
|---|---:|---|---|
| `SPREADSHEET_ID` | Ya | Tidak ada | ID Google Sheets tujuan. |
| `SERVICE_ACCOUNT_FILE` | Tidak | `google-sheets-api.json` | Path file service account Google. |
| `OUTPUT_CSV` | Tidak | `dicoding-fashion-products.csv` | Nama file CSV hasil pipeline. |
| `TOTAL_PAGES` | Tidak | `50` | Jumlah halaman yang akan di-scrape. |
| `EXCHANGE_RATE` | Tidak | `16000` | Kurs konversi dari USD ke IDR. |
| `SHEET_NAME` | Tidak | `Sheet1` | Nama sheet tujuan di Google Sheets. |

Catatan: nilai `TOTAL_PAGES` harus berupa bilangan bulat positif. Nilai `EXCHANGE_RATE` harus lebih besar dari nol.

---

## Instalasi Project

Ikuti langkah berikut untuk menjalankan project secara lokal.

### 1. Clone atau buka folder project

```bash
cd BFPD
```

### 2. Buat virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS atau Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

Isi minimal `requirements.txt`:

```text
requests
beautifulsoup4
pandas
google-api-python-client
google-auth
pytest
pytest-cov
coverage
python-dotenv
```

---

## Cara Menjalankan Pipeline

Jalankan program utama dengan perintah:

```bash
python main.py
```

Jika berhasil, pipeline akan menjalankan proses berikut:

1. Mengambil data produk dari website Fashion Studio Dicoding.
2. Melakukan parsing data mentah dari HTML.
3. Membersihkan data tidak valid.
4. Mengubah harga dari USD ke IDR.
5. Menghapus data duplikat.
6. Menyimpan data ke file CSV.
7. Mengunggah data ke Google Sheets.

---

## Output Data

Output akhir pipeline memiliki struktur kolom berikut.

| Kolom | Tipe Data | Deskripsi |
|---|---|---|
| `Title` | `str` | Nama produk. |
| `Price` | `float` | Harga produk dalam IDR. |
| `Rating` | `float` | Rating produk dalam angka. |
| `Colors` | `int` | Jumlah pilihan warna. |
| `Size` | `str` | Ukuran produk. |
| `Gender` | `str` | Kategori gender produk. |
| `timestamp` | `str` | Waktu data diambil. |

Contoh output CSV:

```csv
Title,Price,Rating,Colors,Size,Gender,timestamp
T-shirt 1,1800000.0,4.5,3,M,Men,2024-01-01 00:00:00
Pants 2,3600000.0,3.8,5,L,Women,2024-01-01 00:00:00
```

---

## Proses Extract

Tahap extract berada di file:

```text
utils/extract.py
```

Fungsi utama pada tahap ini:

| Fungsi | Deskripsi |
|---|---|
| `get_page_url()` | Membuat URL halaman berdasarkan nomor halaman. |
| `extract_price()` | Mengambil harga produk dari elemen HTML. |
| `parse_product_card()` | Mengambil atribut produk dari satu card produk. |
| `scrape_page()` | Mengambil seluruh produk dari satu halaman. |
| `scrape_all_pages()` | Mengambil produk dari banyak halaman. |

Tahap extract menangani beberapa kondisi error, seperti:

- nomor halaman tidak valid,
- timeout,
- connection error,
- HTTP error,
- card produk yang gagal diparse.

---

## Proses Transform

Tahap transform berada di file:

```text
utils/transform.py
```

Fungsi utama pada tahap ini:

| Fungsi | Deskripsi |
|---|---|
| `validate_required_columns()` | Memastikan semua kolom wajib tersedia. |
| `clean_title()` | Menghapus title kosong dan `Unknown Product`. |
| `clean_price()` | Menghapus harga tidak valid dan mengubah USD ke IDR. |
| `clean_rating()` | Mengambil angka rating dari teks rating. |
| `clean_colors()` | Mengambil jumlah warna dalam bentuk integer. |
| `clean_size()` | Menghapus prefix `Size:`. |
| `clean_gender()` | Menghapus prefix `Gender:`. |
| `remove_duplicates()` | Menghapus data duplikat berdasarkan atribut produk. |
| `reset_index()` | Mengatur ulang index DataFrame. |
| `transform()` | Menjalankan seluruh proses transformasi. |

Validasi data yang dilakukan:

- data kosong tidak diproses,
- kolom wajib harus tersedia,
- title kosong dihapus,
- produk `Unknown Product` dihapus,
- price tidak valid dihapus,
- rating tidak valid dihapus,
- colors tidak valid dihapus,
- size kosong dihapus,
- gender kosong dihapus,
- data duplikat dihapus.

---

## Proses Load

Tahap load berada di file:

```text
utils/load.py
```

Fungsi utama pada tahap ini:

| Fungsi | Deskripsi |
|---|---|
| `save_to_csv()` | Menyimpan DataFrame ke file CSV. |
| `get_google_sheets_service()` | Membuat service Google Sheets dari service account. |
| `dataframe_to_sheet_values()` | Mengubah DataFrame menjadi format list untuk Google Sheets. |
| `save_to_google_sheets()` | Menghapus isi sheet lama dan mengunggah data baru. |

Tahap load melakukan validasi terhadap:

- DataFrame kosong,
- spreadsheet ID kosong,
- sheet name kosong,
- file service account tidak ditemukan,
- kegagalan koneksi atau eksekusi Google Sheets API.

---

## Pengujian Unit Test

Jalankan seluruh unit test dengan perintah:

```bash
pytest
```

Untuk output lebih detail:

```bash
pytest -v
```

Daftar test utama:

| File Test | Fokus Pengujian |
|---|---|
| `tests/test_config.py` | Validasi environment variable dan konfigurasi. |
| `tests/test_main.py` | Alur pipeline utama dengan mock dependency. |
| `tests/test_extract.py` | URL generator, parsing HTML, scraping, retry, dan error handling. |
| `tests/test_transform.py` | Validasi kolom, cleaning data, konversi harga, duplikasi, dan error handling. |
| `tests/test_load.py` | Penyimpanan CSV, konversi DataFrame, dan mock Google Sheets API. |

---

## Coverage Test

Coverage digunakan untuk mengukur cakupan pengujian terhadap kode utama.

Konfigurasi `.coveragerc`:

```ini
[run]
source =
    config
    main
    utils

omit =
    tests/*
    */__init__.py
    venv/*

[report]
show_missing = True
fail_under = 100
exclude_lines =
    pragma: no cover
    if __name__ == .__main__.:
```

Jalankan coverage dengan perintah:

```bash
coverage erase
coverage run -m pytest
coverage report -m
```

Alternatif menggunakan `pytest-cov`:

```bash
pytest --cov=config --cov=main --cov=utils --cov-report=term-missing
```

Catatan: folder `tests/` tidak dihitung sebagai target coverage karena folder tersebut berisi kode penguji, bukan kode aplikasi. Coverage yang relevan adalah coverage terhadap `config.py`, `main.py`, dan folder `utils/`.

---

## Keamanan Credential

File credential tidak boleh diunggah ke repository publik.

Tambahkan file berikut ke `.gitignore`:

```gitignore
.env
*.csv
*.json
.coverage
htmlcov/

__pycache__/
.pytest_cache/
.venv/
venv/
*.pyc
.DS_Store
```

Jika project membutuhkan contoh konfigurasi, gunakan file `.env.example`:

```env
SPREADSHEET_ID=your_google_spreadsheet_id
SERVICE_ACCOUNT_FILE=./your_service_account_file.json
OUTPUT_CSV=dicoding-fashion-products.csv
TOTAL_PAGES=50
EXCHANGE_RATE=16000
SHEET_NAME=Sheet1
```

Jangan memasukkan nilai asli `SPREADSHEET_ID` dan service account JSON ke repository publik.

---

## Troubleshooting

### 1. `ValueError: SPREADSHEET_ID is required.`

Penyebab: environment variable `SPREADSHEET_ID` belum tersedia.

Solusi:

- Pastikan file `.env` sudah dibuat.
- Pastikan nama variable ditulis `SPREADSHEET_ID`.
- Pastikan nilainya tidak kosong.

### 2. `Service account file not found`

Penyebab: path file service account salah atau file tidak berada di folder project.

Solusi:

- Cek nilai `SERVICE_ACCOUNT_FILE` di `.env`.
- Pastikan file JSON benar-benar tersedia.
- Jangan ubah nama file tanpa memperbarui `.env`.

### 3. Google Sheets tidak terisi

Penyebab umum:

- Spreadsheet belum dibagikan ke email service account.
- `SPREADSHEET_ID` salah.
- `SHEET_NAME` tidak sesuai.
- Credential Google API tidak valid.

Solusi:

- Buka file JSON service account.
- Salin email service account.
- Bagikan Google Sheets ke email tersebut sebagai editor.
- Jalankan ulang pipeline.

### 4. Coverage Problem

Penyebab umum:

- Ada baris baru yang belum diuji.
- `main.py` belum diimpor oleh test.
- `.coveragerc` belum sesuai.
- Folder yang dihitung coverage terlalu luas.

Solusi:

```bash
coverage erase
coverage run -m pytest
coverage report -m
```

Lihat kolom `Missing`. Tambahkan test untuk baris yang belum tercakup.

### 5. Scraping gagal karena timeout

Penyebab: koneksi lambat atau server tujuan tidak merespons.

Solusi:

- Jalankan ulang pipeline.
- Periksa koneksi internet.
- Naikkan nilai `REQUEST_TIMEOUT` di `utils/extract.py` jika diperlukan.

---

## Project Summary

Project ini menerapkan pipeline ETL secara modular. Setiap tahap dipisahkan ke dalam modul yang spesifik. Tahap extract mengambil data dari website. Tahap transform membersihkan dan mengubah data menjadi format siap pakai. Tahap load menyimpan data ke CSV dan Google Sheets.
