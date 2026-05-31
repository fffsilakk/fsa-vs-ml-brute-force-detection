# Analisis Komparasi Deteksi Serangan Brute Force: FSA vs Machine Learning

Repositori ini memuat kode sumber (_source code_) dan infrastruktur pengujian untuk penelitian komparasi deteksi serangan _Brute Force_ pada sistem otentikasi login. Proyek ini membandingkan kinerja metode konvensional **Finite State Automata (FSA)** dengan dua algoritma _Machine Learning_, yaitu **Decision Tree Classifier** dan **Random Forest Classifier (Ensemble Learning)**.

---

## 📁 Struktur Repositori

Proyek ini dibagi menjadi 3 direktori aplikasi mandiri yang berjalan secara paralel menggunakan _web framework_ Flask dan basis data SQLite:

- **`brute-force-fsa/`**: Implementasi deteksi berbasis matematika transisi status (_state transition_).
- **`brute-force-DecisionTree/`**: Implementasi deteksi berbasis klasifikasi pohon keputusan tunggal.
- **`brute-force-RandomForest/`**: Implementasi deteksi berbasis klasifikasi hutan keputusan acak (_majority voting_).

---

## 🛠️ Spesifikasi Lingkungan Pengujian

Untuk menjalankan seluruh aplikasi ini, pastikan perangkat Anda telah memenuhi dependensi berikut:

- **Python**: Version 3.8 ke atas
- **Library Python Utama**:
  - `Flask` (Web framework)
  - `scikit-learn` (Komputasi model Machine Learning)
  - `pandas` & `numpy` (Pemrosesan matriks data log)
  - `tabulate` (Visualisasi tabel data log pada terminal)

---

## 🚀 Panduan Instalasi dan Pengoperasian

### 1. Kloning Repositori

Buka Terminal atau Command Prompt (CMD), lalu klon repositori ini ke direktori lokal Anda:

```bash
git clone [https://github.com/fffsilakk/fsa-vs-ml-brute-force-detection.git](https://github.com/fffsilakk/fsa-vs-ml-brute-force-detection.git)
cd fsa-vs-ml-brute-force-detection
```

### 2. Instalasi Dependensi (Requirements)

Instal semua pustaka python yang diperlukan menggunakan pip:

```bash
pip install Flask scikit-learn pandas numpy tabulate
```
