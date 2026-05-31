import sqlite3
from tabulate import tabulate  # Pastikan sudah diinstal: pip install tabulate

# KONEKSI KE DATABASE KHUSUS METODE DECISION TREE
DB_NAME = 'brute_force_dt.db'

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("=" * 80)
    print(f"SISTEM MONITORING DATA LOG METODE: DECISION TREE ({DB_NAME})")
    print("=" * 80)

    # --- 1. LIHAT DATA USERS ---
    print("\n" + "-" * 40)
    print("TABEL USERS")
    print("-" * 40)
    cursor.execute('SELECT id, username, created_at FROM users')
    users = cursor.fetchall()
    
    if users:
        print(tabulate(users, headers=['ID', 'Username', 'Created At'], tablefmt='grid'))
    else:
        print("[!] Tidak ada data pengguna yang terdaftar di dalam database.")

    # --- 2. LIHAT LOGIN LOGS (10 TERBARU) ---
    print("\n" + "-" * 40)
    print("TABEL LOGIN LOGS (10 Terbaru)")
    print("-" * 40)
    cursor.execute('''
        SELECT username, success, ip_address, state, message, timestamp 
        FROM login_logs 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    logs = cursor.fetchall()
    
    if logs:
        print(tabulate(logs, headers=['Username', 'Success', 'IP', 'State', 'Message', 'Timestamp'], tablefmt='grid'))
    else:
        print("[!] Belum ada riwayat aktivitas login terdeteksi pada database ini.")

    # --- 3. STATISTIK LOGGER ---
    print("\n" + "-" * 40)
    print("STATISTIK EVALUASI AKTIVITAS")
    print("-" * 40)
    
    # Menggunakan COALESCE agar jika data kosong, Python tidak membaca sebagai 'None' (menghindari error matematika)
    cursor.execute('''
        SELECT 
            COUNT(*),
            COALESCE(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN state = 'blocked' THEN 1 ELSE 0 END), 0)
        FROM login_logs
    ''')
    stats = cursor.fetchone()
    
    print(f"Total Percobaan Akses     : {stats[0]}")
    print(f"Login Sukses (Valid)       : {stats[1]}")
    print(f"Login Gagal (Invalid)      : {stats[2]}")
    print(f"Total Terblokir (Blocked)  : {stats[3]}")

except sqlite3.OperationalError as e:
    print(f"\n[Database Error]: {e}")
    print("[Solusi]: Silakan jalankan file 'app.py' terlebih dahulu atau picu pembuatan database baru.")

finally:
    if 'conn' in locals():
        conn.close()