Dashboard visualisasi dan klasifikasi kejadian **diare akut pada balita**, dibangun sebagai proyek terintegrasi mata kuliah **Data Analitik** dan **Data Science** (Institut Teknologi Del, Semester Ganjil 2026/2027).

> Status: **dalam pengembangan**. Dashboard dan pengelolaan data sudah berjalan. Data warehouse, ETL, dan model klasifikasi final masih dalam pengerjaan (lihat [Status Pengerjaan](#status-pengerjaan)).

## Tujuan

Membantu pengambil keputusan di bidang kesehatan melihat pola kejadian diare balita menurut **wilayah, waktu, dan kelompok usia**, serta hubungannya dengan **indikator sanitasi lingkungan dan kesehatan keluarga**.

Pertanyaan analitik yang dijawab:
1. Wilayah dan kelompok usia mana yang paling terdampak?
2. Kapan kasus meningkat sepanjang tahun?
3. Indikator sanitasi apa yang paling berkaitan dengan tingginya kasus?
4. Apakah kondisi sebuah balita/keluarga tergolong berisiko diare? (modul klasifikasi)

## Fitur

- **Dashboard ringkasan:** kartu KPI dengan pembanding tahun sebelumnya, tren bulanan, distribusi kasus menurut usia, dan peringkat kecamatan berisiko.
- **Analisis wilayah:** treemap, peta sebaran, box plot, dan heatmap usia × bulan.
- **Analisis sanitasi:** bubble chart animasi, korelasi indikator, dan parallel coordinates.
- **Prediksi:** form input kondisi balita dan keluarga, menghasilkan kelas dan probabilitas.
- **Kelola data:** tambah data manual, tambah daerah (kabupaten/kecamatan), impor CSV, hapus data.
- **Data & laporan:** tabel data terfilter, statistik ringkas, dan ekspor CSV.
- Filter global: wilayah, tahun, dan kelompok usia.

## Teknologi

| Lapisan                       | Teknologi                                                            |
|                               |                                                                      |
| Aplikasi & dashboard          | Python, Streamlit, Plotly, Pandas                                    |
| Penyimpanan data (saat ini)   | File CSV di folder `data/`                                           |
| Backend API (opsional)        | Go, SQLite (`modernc.org/sqlite`)                                    |
| Model                         | scikit-learn (Logistic Regression, Random Forest, Gradient Boosting) |

## Struktur Folder

```
.
├── app/
│   ├── dashboard_admin.py     # Aplikasi utama (dashboard + kelola data + prediksi)
│   ├── logo.png               # Logo yang tampil di sidebar
│   ├── dashboard_statis.py    # Versi demo lama (opsional)
│   ├── dashboard_ramah.py     # Versi demo lama (opsional)
│   └── streamlit_app.py       # Versi yang terhubung ke backend Go (opsional)
├── data/                      # Dibuat otomatis saat data pertama kali diinput
│   ├── data_kasus.csv
│   └── wilayah.csv
├── etl/etl.py                 # Skrip ETL ke skema bintang (SQLite)
├── notebooks/train.py         # Pelatihan dan perbandingan 3 model
├── main.go, go.mod            # Backend API Go (opsional)
├── model.json                 # Koefisien model untuk halaman Prediksi
├── Dockerfile                 # Untuk deploy backend Go
├── .streamlit/config.toml     # Tema tampilan
├── requirements.txt           # Dependensi dashboard
└── requirements-ml.txt        # Dependensi untuk pelatihan model
```

## Cara Menjalankan

Prasyarat: Python 3.10 atau lebih baru (disarankan 3.12 atau 3.13).

```bash
# 1. (Disarankan) buat virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1

# 2. Pasang dependensi
python -m pip install -r requirements.txt

# 3. Jalankan aplikasi
python -m streamlit run app/dashboard_admin.py
```

Buka alamat yang tampil di terminal (biasanya `http://localhost:8501`).

Saat pertama dijalankan **aplikasi masih kosong**. Isi data lewat menu **Kelola Data**.

> Jangan beri nama file atau folder proyek `streamlit`, `plotly`, `pandas`, atau `numpy`. Nama itu akan menimpa library dan menyebabkan error impor.

## Mengisi Data

Semua data berasal dari input di dashboard, tidak ada data bawaan di dalam kode.

**Manual:** menu *Kelola Data* → *Tambah daerah* → *Tambah data kasus*.

**Impor CSV:** menu *Kelola Data* → *Impor CSV*. Unduh template, isi, lalu unggah.

| Kolom | Keterangan |
|---|---|
| `kabupaten`, `kecamatan` | Nama wilayah |
| `tahun`, `bulan` | Periode (bulan 1–12) |
| `usia` | Salah satu: `0-11 bln`, `12-23 bln`, `24-35 bln`, `36-47 bln`, `48-59 bln` |
| `balita` | Jumlah balita yang diperiksa |
| `kasus` | Jumlah kasus diare (tidak boleh melebihi `balita`) |
| `jamban`, `air`, `cuci`, `asi` | Persentase 0–100: jamban sehat, air bersih, cuci tangan pakai sabun, ASI eksklusif |
| `lat`, `lon` | *Opsional*, koordinat untuk peta |

Baris dengan kombinasi `kabupaten + kecamatan + tahun + bulan + usia` yang sama akan memperbarui data lama. Baris yang tidak valid ditolak dan jumlahnya ditampilkan.

## Model Klasifikasi

Halaman **Prediksi** membaca koefisien Logistic Regression dari `model.json`.

> Isi `model.json` saat ini hanya **placeholder**. Jangan dipakai sebagai hasil model yang sebenarnya.

Untuk melatih model dari data sendiri:

```bash
python -m pip install -r requirements-ml.txt
python etl/etl.py            # memuat data/raw.csv ke diare.db (skema bintang)
python notebooks/train.py    # melatih 3 model, mencetak F1 dan AUC, menulis model.json
```

Skrip `etl.py` dan `train.py` mengharapkan kolom tertentu pada data mentah. Sesuaikan nama kolomnya dengan dataset yang dipakai.

## Backend Go (opsional)

Backend Go menyediakan API ringkasan data dari database SQLite dan endpoint prediksi. Aplikasi utama (`dashboard_admin.py`) **tidak** memerlukannya.

```bash
go mod tidy
go run .                                         # http://localhost:8080
python -m streamlit run app/streamlit_app.py     # dashboard yang memakai API tersebut
```

Endpoint: `/api/filters`, `/api/summary`, `/api/by?dim=...`, `/api/risk`, `POST /api/predict`.

## Deployment

- **Aplikasi Streamlit:** dapat di-deploy ke Streamlit Community Cloud dengan file utama `app/dashboard_admin.py`.
- **Backend Go:** dapat di-deploy ke Render atau Railway menggunakan `Dockerfile`.
- Penyimpanan CSV di Streamlit Community Cloud **tidak permanen** dan bisa hilang saat aplikasi restart. Untuk penggunaan publik, hubungkan ke database (misalnya PostgreSQL).
- Halaman *Kelola Data* belum memiliki autentikasi. Tambahkan login sebelum dipublikasikan.

## Status Pengerjaan

- [x] Dashboard interaktif dengan filter global
- [x] Pengelolaan data manual dan impor CSV
- [x] Halaman prediksi (antarmuka)
- [ ] Dataset asli dan dokumentasinya (data dictionary, laporan kualitas data)
- [ ] ETL dan data warehouse skema bintang
- [ ] Pelatihan, tuning, dan evaluasi model (≥ 3 algoritma), model card
- [ ] Deployment publik
- [ ] Uji kegunaan dengan calon pengguna

## Sumber Data dan Etika

- Sumber data: **[isi nama sumber dan tautan/izin]**
- Data pribadi harus dianonimkan sesuai UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi.
- Data yang diunggah ke dashboard hanya boleh berasal dari sumber yang berizin.


Dosen pengampu: Oppir Hutapea, M.Kom
