# 🕌 SunnahSearch - Information Retrieval (Streamlit Edition)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sunnahsearch---information-retrieval.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)

> **Sistem Temu Kembali Informasi (Search Engine) untuk Hadits menggunakan Algoritma BM25.**

---

## 📖 Tentang Projek

**SunnahSearch** adalah aplikasi mesin pencari (search engine) berbasis web yang dikembangkan untuk memudahkan pengguna dalam menelusuri ribuan koleksi Hadits dan Sunnah.

Projek ini dibuat sebagai **Final Project** mata kuliah **Information Retrieval (Temu Kembali Informasi)**. Sistem ini dibangun menggunakan framework **Streamlit** dan mengimplementasikan algoritma **Okapi BM25** (Best Matching 25) untuk melakukan *ranking* dokumen, memastikan hasil pencarian yang muncul adalah yang paling relevan dengan kata kunci pengguna.

### 🧮 Algoritma: BM25
Sistem ini menghitung skor relevansi berdasarkan probabilitas kemunculan kata dalam dokumen (Hadits) dibandingkan dengan keseluruhan koleksi data, memberikan hasil yang lebih akurat dibanding pencarian teks biasa.

---

## 📂 Dataset

Data yang digunakan dalam aplikasi ini bersumber dari Kaggle:
* **Nama Dataset:** Sunnah Dataset (`Sunnah.csv`)
* **Sumber:** [Kaggle - Ronnie Aban Sunnah Dataset](https://www.kaggle.com/datasets/ronnieaban/sunnah)
* **Konten:** Berisi teks Hadits dalam Bahasa Arab, Terjemahan (Indonesia/Inggris), dan Nama Perawi.

---

## ✨ Fitur Utama

Aplikasi ini dilengkapi dengan berbagai fitur interaktif:

* **🔍 Search Engine Hadits:** Pencarian cepat dan akurat menggunakan indexing BM25.
* **⚡ Mode Pencarian Fleksibel:**
    1.  **Pencarian Umum:** Mencari kata kunci di seluruh database (Arab & Terjemahan).
    2.  **Perawi Spesifik:** Menampilkan seluruh hadits dari perawi tertentu (misal: Bukhari, Muslim).
    3.  **Kombinasi (Teks & Perawi):** Mencari topik tertentu (misal: "puasa") hanya di dalam koleksi perawi tertentu.
* **🎚️ Filter Hasil:** Batasi jumlah hasil yang ditampilkan per halaman (5, 15, 30, 50, atau Semua).
* **📱 Responsif & Modern:** Antarmuka yang bersih dan otomatis menyesuaikan tema (Light/Dark Mode).

---

## 📸 Dokumentasi (Screenshots)

Berikut adalah tampilan antarmuka aplikasi **SunnahSearch**:

### 1. Tampilan Awal (Beranda)
*Halaman utama dengan kolom pencarian yang bersih dan opsi filter.*
<img src="https://github.com/user-attachments/assets/15c8d454-262e-42c0-84f8-45931c501bb8" alt="Tampilan Awal SunnahSearch" width="800" />

---

### 2. Hasil Pencarian
*Menampilkan teks Arab, Terjemahan, dan Skor Relevansi BM25.*
<img src="https://github.com/user-attachments/assets/de06554b-660a-4fe7-a54d-b624dbd25ef3" alt="Hasil Pencarian Hadits" width="800" />

---

### 3. Halaman Tentang
*Informasi mengenai pengembang dan dataset.*
<img src="https://github.com/user-attachments/assets/8f118d05-2309-4cfe-adde-0a4eb371180b" alt="Halaman Tentang" width="800" />

---

## 🛠️ Instalasi & Cara Menjalankan

Jika Anda ingin menjalankan projek ini di komputer lokal Anda, ikuti langkah berikut:

1.  **Clone Repository**
    ```bash
    git clone [https://github.com/aliridwan15/SunnahSearch---Information-Retrieval---Streamlite.git](https://github.com/aliridwan15/SunnahSearch---Information-Retrieval---Streamlite.git)
    cd SunnahSearch---Information-Retrieval---Streamlite
    ```

2.  **Install Library yang Dibutuhkan**
    Pastikan Python sudah terinstal, lalu jalankan:
    ```bash
    pip install streamlit pandas rank_bm25
    ```

3.  **Jalankan Aplikasi**
    Gunakan perintah `streamlit run` (bukan python):
    ```bash
    streamlit run app.py
    ```

4.  **Buka di Browser**
    Aplikasi akan otomatis terbuka di browser, biasanya di alamat:
    `http://localhost:8501`

---

## 👨‍💻 Tim Pengembang

Projek ini dikembangkan oleh:

| Nama | NIM | Peran |
| :--- | :--- | :--- |
| **Ali Ridwan Nurhasan** | **230411100154** | **Fullstack Developer** |

---

<div align="center">
  <small>Dibuat dengan ❤️ untuk Tugas Information Retrieval</small>
</div>
