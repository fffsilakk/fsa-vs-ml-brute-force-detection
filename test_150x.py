# import threading
# import time
# import requests

# # Konfigurasi target endpoint port paralel Anda
# TARGETS = {
#     "FSA (Port 5000)": "http://localhost:5000/login",
#     "Decision Tree (Port 5001)": "http://localhost:5001/login",
#     "Random Forest (Port 5002)": "http://localhost:5002/login",
# }


# def kirim_request(url, username, password):
#     try:
#         # Menembak form login secara background via POST request
#         requests.post(
#             url, data={"username": username, "password": password}, timeout=2
#         )
#     except Exception:
#         pass


# def jalankan_simulasi_150x(metode_name, url):
#     print(f"\n🚀 Memulai simulasi 150x request untuk {metode_name}...")
#     threads = []

#     start_time = time.time()

#     # 1. Simulasikan 120 Request Serangan Brute Force (Kredensial Salah)
#     for i in range(120):
#         t = threading.Thread(
#             target=kirim_request, args=(url, f"attacker_{i}", "salah_pass123")
#         )
#         threads.append(t)
#         t.start()
#         time.sleep(0.005)  # Jeda mikro agar tidak merusak antrean port lock

#     # 2. Simulasikan 30 Request Login Pengguna Sah (Kredensial Benar)
#     for _ in range(30):
#         t = threading.Thread(target=kirim_request, args=(url, "admin", "admin123"))
#         threads.append(t)
#         t.start()
#         time.sleep(0.005)

#     # Tunggu semua thread selesai menembak backend
#     for t in threads:
#         t.join()

#     end_time = time.time()
#     print(
#         f"✓ {metode_name} selesai memproses 150 data dalam {end_time - start_time:.3f} detik!"
#     )


# if __name__ == "__main__":
#     print("=" * 70)
#     # Jalankan simulasi otomatis ke ketiga aplikasi Flask yang sedang aktif
#     for nama_metode, endpoint_url in TARGETS.items():
#         jalankan_simulasi_150x(nama_metode, endpoint_url)
#     print("=" * 70)
#     print(
#         "⚡ Selesai! Silakan cek web dashboard atau jalankan 'python view_database.py' pada tiap folder!"
#     )


import threading
import time
import requests

# Konfigurasi target endpoint port paralel Anda
TARGETS = {
    "FSA (Port 5000)": "http://localhost:5000/login",
}


def kirim_request(url, username, password):
    try:
        # Menembak form login secara background via POST request
        requests.post(
            url, data={"username": username, "password": password}, timeout=2
        )
    except Exception:
        pass


def jalankan_simulasi_20x(metode_name, url):
    print(f"\n🚀 Memulai simulasi 20x request untuk {metode_name}...")
    threads = []

    start_time = time.time()

    # 1. Simulasikan 6 Request Serangan Brute Force (Kredensial Salah)
    # Ini akan memicu state SUSPICIOUS pada hitungan ke-3 dan BLOCKED pada hitungan ke-5
    for i in range(6):
        t = threading.Thread(
            target=kirim_request, args=(url, f"attacker_{i}", "salah_pass123")
        )
        threads.append(t)
        t.start()
        time.sleep(0.005)  # Jeda mikro agar tidak merusak antrean port lock

    # 2. Simulasikan 14 Request Login Pengguna Sah (Kredensial Benar)
    # Ini untuk mencatat 14 transaksi sukses di database Anda
    for _ in range(14):
        t = threading.Thread(target=kirim_request, args=(url, "admin", "admin123"))
        threads.append(t)
        t.start()
        time.sleep(0.005)

    # Tunggu semua thread selesai menembak backend
    for t in threads:
        t.join()

    end_time = time.time()
    print(
        f"✓ {metode_name} selesai memproses 20 data dalam {end_time - start_time:.3f} detik!"
    )


if __name__ == "__main__":
    print("=" * 70)
    # Jalankan simulasi otomatis ke aplikasi Flask yang sedang aktif
    for nama_metode, endpoint_url in TARGETS.items():
        jalankan_simulasi_20x(nama_metode, endpoint_url)
    print("=" * 70)
    print(
        "⚡ Selesai! Silakan cek web dashboard atau jalankan 'python view_database.py' pada folder Anda!"
    )