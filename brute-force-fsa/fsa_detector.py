from datetime import datetime, timedelta
from enum import Enum


class State(Enum):
    """Enum untuk state FSA"""
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


class FSADetector:
    """
    Finite State Automata untuk deteksi serangan brute force
    
    FEATURES:
    - HYBRID TRACKING: Username + IP Address
    - FORGIVING MODE: Unblock jika password benar saat blocked
    - MULTI-LAYER SECURITY: Proteksi ganda
    
    State:
    - NORMAL: Kondisi normal, tidak ada indikasi serangan
    - SUSPICIOUS: Terdeteksi percobaan login gagal berulang (≥ 3x)
    - BLOCKED: Akun/IP diblokir karena terdeteksi serangan brute force (≥ 5x)
    """
    
    def __init__(self, max_attempts=5, time_window=60, block_duration=300):
        """
        Inisialisasi FSA Detector
        
        Args:
            max_attempts: Jumlah maksimal percobaan gagal (default: 5)
            time_window: Window waktu dalam detik untuk menghitung percobaan (default: 60)
            block_duration: Durasi pemblokiran dalam detik (default: 300/5 menit)
        """
        self.max_attempts = max_attempts
        self.time_window = time_window
        self.block_duration = block_duration
        self.suspicious_threshold = 3  # Threshold untuk state suspicious
        
        # Storage untuk tracking percobaan login
        self.username_attempts = {}   # {username: [(timestamp, success, ip), ...]}
        self.ip_attempts = {}          # {ip_address: [(timestamp, success, username), ...]}
        self.blocked_usernames = {}    # {username: blocked_until_timestamp}
        self.blocked_ips = {}          # {ip_address: blocked_until_timestamp}
    
    def get_state(self, username, ip_address):
        """
        Mendapatkan state saat ini berdasarkan username DAN IP address
        
        Args:
            username: Username yang diperiksa
            ip_address: IP address yang diperiksa
            
        Returns:
            tuple: (State, reason) - State saat ini dan alasan
        """
        now = datetime.now()
        
        # Cek apakah username sedang diblokir
        if username in self.blocked_usernames:
            blocked_until = self.blocked_usernames[username]
            if now < blocked_until:
                return State.BLOCKED, "username"
            else:
                # Unblock username jika waktu blokir sudah habis
                del self.blocked_usernames[username]
                if username in self.username_attempts:
                    self.username_attempts[username] = []
        
        # Cek apakah IP sedang diblokir
        if ip_address in self.blocked_ips:
            blocked_until = self.blocked_ips[ip_address]
            if now < blocked_until:
                return State.BLOCKED, "ip"
            else:
                # Unblock IP jika waktu blokir sudah habis
                del self.blocked_ips[ip_address]
                if ip_address in self.ip_attempts:
                    self.ip_attempts[ip_address] = []
        
        # Hitung jumlah percobaan gagal
        username_failed = self._count_failed_attempts(username, self.username_attempts)
        ip_failed = self._count_failed_attempts(ip_address, self.ip_attempts)
        
        # Ambil nilai tertinggi (yang paling berbahaya)
        max_failed = max(username_failed, ip_failed)
        
        # Tentukan reason berdasarkan mana yang lebih tinggi
        if username_failed >= ip_failed:
            reason = "username"
        else:
            reason = "ip"
        
        # Tentukan state berdasarkan jumlah percobaan gagal
        if max_failed >= self.max_attempts:
            return State.BLOCKED, reason
        elif max_failed >= self.suspicious_threshold:
            return State.SUSPICIOUS, reason
        else:
            return State.NORMAL, reason
    
    def record_login_attempt(self, username, ip_address, success):
        """
        Mencatat percobaan login dan melakukan transisi state
        FORGIVING MODE: Jika password benar saat BLOCKED, unblock dan allow login
        
        Args:
            username: Username yang mencoba login
            ip_address: IP address yang mencoba login
            success: Boolean, True jika login berhasil, False jika gagal
            
        Returns:
            dict: Status hasil dengan state, message, dan blocked_until (jika ada)
        """
        now = datetime.now()
        
        # Inisialisasi list jika belum ada
        if username not in self.username_attempts:
            self.username_attempts[username] = []
        if ip_address not in self.ip_attempts:
            self.ip_attempts[ip_address] = []
        
        # Dapatkan state saat ini SEBELUM record attempt
        current_state, reason = self.get_state(username, ip_address)
        
        # ============================================
        # FORGIVING MODE: Jika login BERHASIL saat BLOCKED
        # ============================================
        if success and current_state == State.BLOCKED:
            # Unblock username dan IP
            if username in self.blocked_usernames:
                del self.blocked_usernames[username]
                print(f"✓ Username '{username}' di-unblock karena login berhasil")
            
            if ip_address in self.blocked_ips:
                del self.blocked_ips[ip_address]
                print(f"✓ IP '{ip_address}' di-unblock karena login berhasil")
            
            # Reset attempts
            self.username_attempts[username] = []
            self.ip_attempts[ip_address] = []
            
            # Add successful login
            self.username_attempts[username].append((now, True, ip_address))
            self.ip_attempts[ip_address].append((now, True, username))
            
            return {
                'state': State.NORMAL,
                'message': 'Login berhasil. Akun/IP telah di-unblock.',
                'blocked': False,
                'reason': None,
                'unblocked': True  # Flag bahwa user di-unblock
            }
        
        # Tambahkan percobaan login ke KEDUA tracker
        self.username_attempts[username].append((now, success, ip_address))
        self.ip_attempts[ip_address].append((now, success, username))
        
        # Bersihkan percobaan yang sudah lewat dari time window
        self._cleanup_old_attempts(username, self.username_attempts)
        self._cleanup_old_attempts(ip_address, self.ip_attempts)
        
        # Re-calculate state setelah record attempt
        current_state, reason = self.get_state(username, ip_address)
        
        # Jika login berhasil dan state bukan BLOCKED
        if success and current_state != State.BLOCKED:
            # Reset attempts
            self.username_attempts[username] = []
            self.ip_attempts[ip_address] = []
            
            return {
                'state': State.NORMAL,
                'message': 'Login berhasil',
                'blocked': False,
                'reason': None
            }
        
        # Jika sudah BLOCKED (login gagal)
        if current_state == State.BLOCKED:
            blocked_until = now + timedelta(seconds=self.block_duration)
            
            # Block berdasarkan reason
            if reason == "username":
                self.blocked_usernames[username] = blocked_until
                message = f'Username "{username}" diblokir karena terlalu banyak percobaan gagal. Coba lagi setelah {self.block_duration} detik atau masukkan password yang benar.'
            else:  # reason == "ip"
                self.blocked_ips[ip_address] = blocked_until
                message = f'IP Address Anda diblokir karena terlalu banyak percobaan gagal. Coba lagi setelah {self.block_duration} detik atau masukkan password yang benar.'
            
            return {
                'state': State.BLOCKED,
                'message': message,
                'blocked': True,
                'blocked_until': blocked_until,
                'reason': reason
            }
        
        # State SUSPICIOUS
        elif current_state == State.SUSPICIOUS:
            username_failed = self._count_failed_attempts(username, self.username_attempts)
            ip_failed = self._count_failed_attempts(ip_address, self.ip_attempts)
            max_failed = max(username_failed, ip_failed)
            remaining = self.max_attempts - max_failed
            
            if reason == "username":
                message = f'Peringatan: {username_failed} percobaan gagal untuk username "{username}". {remaining} percobaan tersisa sebelum akun diblokir.'
            else:  # reason == "ip"
                message = f'Peringatan: {ip_failed} percobaan gagal dari IP Anda. {remaining} percobaan tersisa sebelum diblokir.'
            
            return {
                'state': State.SUSPICIOUS,
                'message': message,
                'blocked': False,
                'failed_attempts': max_failed,
                'remaining_attempts': remaining,
                'reason': reason
            }
        
        # State NORMAL
        else:
            return {
                'state': State.NORMAL,
                'message': 'Username atau password salah',
                'blocked': False,
                'reason': None
            }
    
    def _count_failed_attempts(self, identifier, attempts_dict):
        """
        Menghitung jumlah percobaan gagal dalam time window
        
        Args:
            identifier: Username atau IP address yang diperiksa
            attempts_dict: Dictionary attempts (username_attempts atau ip_attempts)
            
        Returns:
            int: Jumlah percobaan gagal
        """
        if identifier not in attempts_dict:
            return 0
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.time_window)
        
        failed_count = 0
        for timestamp, success, _ in attempts_dict[identifier]:
            if timestamp >= cutoff_time and not success:
                failed_count += 1
        
        return failed_count
    
    def _cleanup_old_attempts(self, identifier, attempts_dict):
        """
        Membersihkan percobaan login yang sudah lewat dari time window
        
        Args:
            identifier: Username atau IP address yang akan dibersihkan
            attempts_dict: Dictionary attempts (username_attempts atau ip_attempts)
        """
        if identifier not in attempts_dict:
            return
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.time_window)
        
        # Filter hanya percobaan dalam time window
        attempts_dict[identifier] = [
            (timestamp, success, extra_info) 
            for timestamp, success, extra_info in attempts_dict[identifier]
            if timestamp >= cutoff_time
        ]
    
    def get_statistics(self, username=None, ip_address=None):
        """
        Mendapatkan statistik percobaan login
        
        Args:
            username: Username yang diperiksa (optional)
            ip_address: IP address yang diperiksa (optional)
            
        Returns:
            dict: Statistik login attempts
        """
        if username and username in self.username_attempts:
            failed = self._count_failed_attempts(username, self.username_attempts)
            total = len([a for a in self.username_attempts[username] 
                        if a[0] >= datetime.now() - timedelta(seconds=self.time_window)])
            successful = total - failed
            current_state, _ = self.get_state(username, ip_address or "0.0.0.0")
            
            return {
                'total_attempts': total,
                'failed_attempts': failed,
                'successful_attempts': successful,
                'current_state': current_state.value,
                'tracking': 'username'
            }
        
        if ip_address and ip_address in self.ip_attempts:
            failed = self._count_failed_attempts(ip_address, self.ip_attempts)
            total = len([a for a in self.ip_attempts[ip_address] 
                        if a[0] >= datetime.now() - timedelta(seconds=self.time_window)])
            successful = total - failed
            current_state, _ = self.get_state(username or "", ip_address)
            
            return {
                'total_attempts': total,
                'failed_attempts': failed,
                'successful_attempts': successful,
                'current_state': current_state.value,
                'tracking': 'ip_address'
            }
        
        return {
            'total_attempts': 0,
            'failed_attempts': 0,
            'successful_attempts': 0,
            'current_state': State.NORMAL.value,
            'tracking': 'none'
        }
    
    def get_detailed_stats(self):
        """
        Mendapatkan statistik lengkap sistem
        
        Returns:
            dict: Statistik lengkap termasuk blocked items
        """
        return {
            'total_tracked_usernames': len(self.username_attempts),
            'total_tracked_ips': len(self.ip_attempts),
            'blocked_usernames': list(self.blocked_usernames.keys()),
            'blocked_ips': list(self.blocked_ips.keys()),
            'total_blocked_usernames': len(self.blocked_usernames),
            'total_blocked_ips': len(self.blocked_ips)
        }
    
    def manual_unblock(self, username=None, ip_address=None):
        """
        Manually unblock username atau IP address
        Useful untuk admin intervention
        
        Args:
            username: Username yang akan di-unblock (optional)
            ip_address: IP address yang akan di-unblock (optional)
            
        Returns:
            dict: Status unblock operation
        """
        unblocked_items = []
        
        if username and username in self.blocked_usernames:
            del self.blocked_usernames[username]
            self.username_attempts[username] = []
            unblocked_items.append(f"username: {username}")
        
        if ip_address and ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            self.ip_attempts[ip_address] = []
            unblocked_items.append(f"IP: {ip_address}")
        
        if unblocked_items:
            return {
                'success': True,
                'message': f"Successfully unblocked: {', '.join(unblocked_items)}",
                'unblocked': unblocked_items
            }
        else:
            return {
                'success': False,
                'message': "No items to unblock",
                'unblocked': []
            }
    
    def reset_all(self):
        """
        Reset semua data tracking (untuk testing atau emergency)
        
        Returns:
            dict: Status reset operation
        """
        self.username_attempts.clear()
        self.ip_attempts.clear()
        self.blocked_usernames.clear()
        self.blocked_ips.clear()
        
        return {
            'success': True,
            'message': 'All tracking data has been reset'
        }
