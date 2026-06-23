# 🚀 Simulator Kebijakan Keuntungan Toko

Simulator Kebijakan Keuntungan Toko adalah aplikasi web interaktif berbasis **Streamlit** yang digunakan untuk mensimulasikan dampak perubahan kebijakan bisnis terhadap proyeksi keuntungan toko. Aplikasi ini menerapkan konsep **What-If Analysis**, **Policy Simulation**, dan **Machine Learning** untuk membantu pengguna mengevaluasi berbagai skenario sebelum mengambil keputusan.

Melalui simulator ini, pengguna dapat mengubah variabel kontrol seperti **Anggaran Iklan** dan **Besaran Diskon**, kemudian mengamati perubahan prediksi keuntungan secara real-time berdasarkan model Machine Learning yang telah dilatih sebelumnya.

## 📌 Fitur Utama

### 1. What-If Analysis

* Menggunakan slider interaktif untuk mengatur Anggaran Iklan dan Besaran Diskon.
* Membandingkan kondisi saat ini (**Baseline**) dengan skenario baru (**Intervensi**).
* Menampilkan prediksi keuntungan secara real-time.
* Menghitung perubahan (Delta Analysis) terhadap kondisi awal.
* Memberikan rekomendasi otomatis berdasarkan hasil simulasi.

### 2. Profit Heatmap

* Memvisualisasikan potensi keuntungan dari berbagai kombinasi Iklan dan Diskon.
* Menampilkan titik profit maksimum (Optimal Point).
* Menunjukkan posisi skenario yang sedang dijalankan pengguna.
* Membantu mengidentifikasi kombinasi kebijakan yang paling menguntungkan.

### 3. Scenario Leaderboard

* Menyimpan skenario simulasi yang telah diuji.
* Menampilkan peringkat skenario berdasarkan profit tertinggi.
* Memudahkan pengguna membandingkan berbagai alternatif kebijakan.
* Mendukung penghapusan skenario tertentu maupun seluruh riwayat simulasi.

## 🛠️ Teknologi yang Digunakan

* Python 3
* Streamlit
* Pandas
* NumPy
* Matplotlib
* Scikit-Learn
* Joblib

## 🚀 Menjalankan Aplikasi Secara Lokal

### 1. Clone Repository

```bash
git clone https://github.com/achmadwachid/simulator-kebijakan-toko.git
```

### 2. Masuk ke Folder Proyek

```bash
cd simulator-kebijakan-toko
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Jalankan Streamlit

```bash
streamlit run app.py
```

Aplikasi akan berjalan pada:

```text
http://localhost:8501
```

## 🌐 Demo Aplikasi

**Live Demo:** https://simulator-kebijakan-toko.streamlit.app