import sqlite3
from tabulate import tabulate  # Install: pip install tabulate

# Koneksi ke database
conn = sqlite3.connect('brute_force_fsa.db')
cursor = conn.cursor()

print("=" * 80)
print("TABEL USERS")
print("=" * 80)

# Lihat data users
cursor.execute('SELECT id, username, created_at FROM users')
users = cursor.fetchall()
print(tabulate(users, headers=['ID', 'Username', 'Created At'], tablefmt='grid'))

print("\n" + "=" * 80)
print("TABEL LOGIN LOGS (10 Terbaru)")
print("=" * 80)

# Lihat login logs
cursor.execute('''
    SELECT username, success, ip_address, state, message, timestamp 
    FROM login_logs 
    ORDER BY timestamp DESC 
    LIMIT 10
''')
logs = cursor.fetchall()
print(tabulate(logs, headers=['Username', 'Success', 'IP', 'State', 'Message', 'Timestamp'], tablefmt='grid'))

print("\n" + "=" * 80)
print("STATISTIK")
print("=" * 80)

# Statistik
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as berhasil,
        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as gagal,
        SUM(CASE WHEN state = 'blocked' THEN 1 ELSE 0 END) as blocked
    FROM login_logs
''')
stats = cursor.fetchone()
print(f"Total Percobaan: {stats[0]}")
print(f"Login Berhasil: {stats[1]}")
print(f"Login Gagal: {stats[2]}")
print(f"State Blocked: {stats[3]}")

conn.close()
