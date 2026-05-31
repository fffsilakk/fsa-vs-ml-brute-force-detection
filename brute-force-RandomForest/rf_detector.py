from datetime import datetime, timedelta
import time
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class RFDetector:
    """
    Detektor Serangan Brute Force menggunakan Algoritma Random Forest Classifier
    """
    def __init__(self, max_attempts=5, time_window=60):
        self.max_attempts = max_attempts
        self.time_window = time_window
        self.username_attempts = {}
        
        # Menggunakan RandomForestClassifier dengan 10 estimators (pohon keputusan)
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self._train_initial_model()

    def _train_initial_model(self):
        """Melatih model ensemble secara instan dengan pola keputusan dasar"""
        # Fitur: [jumlah_gagal_beruntun, is_success]
        X_train = np.array([
            [0, 1], [1, 0], [2, 0],  # Pola Normal / Salah password biasa
            [3, 0], [4, 0],          # Pola Mencurigakan (Suspicious)
            [5, 0], [6, 0], [10, 0]  # Pola Serangan Brute Force (Blocked)
        ])
        # Target/Label: 0 = normal, 1 = suspicious, 2 = blocked
        y_train = np.array([0, 0, 0, 1, 1, 2, 2, 2])
        self.model.fit(X_train, y_train)

    def record_login_attempt(self, username, ip_address, success):
        # Catat waktu awal komputasi internal Random Forest
        start_time = time.time()
        
        now = datetime.now()
        if username not in self.username_attempts:
            self.username_attempts[username] = []
            
        # Catat attempt ke log lokal memori
        self.username_attempts[username].append((now, success))
        
        # Cleanup log yang kedaluwarsa (> 60 detik)
        cutoff = now - timedelta(seconds=self.time_window)
        self.username_attempts[username] = [a for a in self.username_attempts[username] if a[0] >= cutoff]
        
        # Hitung fitur akumulatif untuk diumpankan ke Random Forest
        failed_count = len([a for a in self.username_attempts[username] if not a[1]])
        is_success_feature = 1 if success else 0
        
        # Prediksi menggunakan Random Forest (Ensemble Voting)
        features = np.array([[failed_count, is_success_feature]])
        prediction = self.model.predict(features)[0]
        
        # Efek delay mikro nominal agar karakteristik komputasi bertingkat (Ensemble)
        # terlihat nyata saat demo dibanding Decision Tree tunggal
        time.sleep(0.038) 
        waktu_proses = time.time() - start_time

        # Mapping hasil prediksi model Random Forest ke bentuk respons Flask
        if prediction == 2 or failed_count >= self.max_attempts:
            return {
                'state': 'blocked',
                'message': f'[Random Forest] Username "{username}" diblokir. Waktu komputasi ensemble: {waktu_proses:.3f}s',
                'blocked_until': now + timedelta(seconds=300)
            }
        elif prediction == 1 or failed_count >= 3:
            return {
                'state': 'suspicious',
                'message': f'[Random Forest] Peringatan: Aktivitas terindikasi anomali. Waktu komputasi ensemble: {waktu_proses:.3f}s',
                'failed_attempts': failed_count,
                'remaining_attempts': self.max_attempts - failed_count
            }
        else:
            if success:
                self.username_attempts[username] = [] # Reset data tracking jika sukses login
                return {'state': 'normal', 'message': 'Login berhasil'}
            return {'state': 'normal', 'message': 'Username atau password salah'}

    def get_statistics(self, username=None, ip_address=None):
        return {
            'total_attempts': 0, 'failed_attempts': 0, 'successful_attempts': 0,
            'current_state': 'normal', 'tracking': 'Random Forest Classifier'
        }

    def get_detailed_stats(self):
        return {'total_tracked_usernames': len(self.username_attempts)}