import sqlite3
from datetime import datetime
import hashlib

class Database:
    """Kelas untuk manajemen database user dan log"""
    
    # UBAH BARIS INI: Ganti brute_force_fsa.db menjadi brute_force_dt.db
    def __init__(self, db_name='brute_force_dt.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inisialisasi database dan tabel"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabel users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel login_logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                ip_address TEXT,
                state TEXT NOT NULL,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert user demo jika belum ada
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # Password: admin123 (hashed)
            hashed_password = self.hash_password('admin123')
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                ('admin', hashed_password)
            )
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password menggunakan SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, username, password):
        """
        Verifikasi username dan password
        
        Returns:
            bool: True jika credentials benar, False jika salah
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        hashed_password = self.hash_password(password)
        cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password = ?',
            (username, hashed_password)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def log_login_attempt(self, username, success, ip_address, state, message):
        """Mencatat percobaan login ke database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO login_logs (username, success, ip_address, state, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, success, ip_address, state, message))
        
        conn.commit()
        conn.close()
    
    def get_login_logs(self, limit=100):
        """Mengambil log login terbaru"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, success, ip_address, state, message, timestamp
            FROM login_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return logs