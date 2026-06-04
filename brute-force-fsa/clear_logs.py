import sqlite3

# Sesuaikan nama file database Anda, biasanya 'database.db' atau 'auth.db'
# Jika nama databasenya berbeda, silakan ganti teks di bawah ini
DB_NAME = "brute_force_fsa.db"

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Menghapus seluruh isi tabel login logs
    cursor.execute("DELETE FROM login_logs;")
    
    # Opsional: Jika ada tabel 'failed_logins' atau 'blocked_ips' untuk tracking state, kosongkan juga
    # cursor.execute("DELETE FROM failed_logins;")
    
    conn.commit()
    print("==========================================================")
    print("⚡ BERHASIL: Tabel LOGIN LOGS telah dikosongkan!")
    print("👤 Data user 'admin' tetap aman di tabel USERS.")
    print("==========================================================")
except Exception as e:
    print(f"❌ Terjadi kesalahan: {e}")
finally:
    conn.close()