from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from rf_detector import RFDetector
from database import Database
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Inisialisasi Random Forest Detector dan Database Khusus RF
rf_detector = RFDetector(max_attempts=5, time_window=60)
db = Database()


@app.route('/')
def index():
    """Halaman utama - redirect ke login"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login - Menggunakan Deteksi Random Forest"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        ip_address = request.remote_addr
        
        # Verifikasi credentials ke SQLite
        is_valid = db.verify_credentials(username, password)
        
        # Record login attempt dengan model Random Forest
        result = rf_detector.record_login_attempt(username, ip_address, is_valid)
        
        # Ambil nilai string state hasil prediksi ('normal', 'suspicious', 'blocked')
        current_state = result['state']
        
        # Log ke database log lokal (brute_force_rf.db)
        db.log_login_attempt(username, is_valid, ip_address,
                             current_state, result['message'])
        
        # Handle berdasarkan hasil prediksi model Random Forest
        if is_valid and current_state != 'blocked':
            # Login berhasil dan tidak diblokir oleh Random Forest
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        elif current_state == 'blocked':
            # Hasil prediksi: BLOCKED
            return render_template('blocked.html',
                                   blocked_until=result.get('blocked_until'),
                                   message=result['message'],
                                   reason=result.get('reason', 'username'))
        
        else:
            # Hasil prediksi: NORMAL (gagal password biasa) atau SUSPICIOUS
            return render_template('login.html',
                                   error=result['message'],
                                   state=current_state,
                                   failed_attempts=result.get('failed_attempts', 0),
                                   remaining_attempts=result.get('remaining_attempts', 0),
                                   reason=result.get('reason', 'username'),
                                   unblocked=result.get('unblocked', False))
    
    # GET request
    return render_template('login.html', state='normal')


@app.route('/dashboard')
def dashboard():
    """Halaman dashboard setelah login berhasil"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    ip_address = request.remote_addr
    
    # Ambil statistik dari modul Random Forest
    stats = rf_detector.get_statistics(username=username, ip_address=ip_address)
    detailed_stats = rf_detector.get_detailed_stats()
    logs = db.get_login_logs(limit=50)
    
    return render_template('dashboard.html', 
                           username=username,
                           stats=stats,
                           detailed_stats=detailed_stats,
                           logs=logs)


@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/api/stats/<username>')
def api_stats(username):
    """API endpoint untuk mendapatkan statistik berbasis Random Forest"""
    ip_address = request.remote_addr
    stats = rf_detector.get_statistics(username=username, ip_address=ip_address)
    return jsonify(stats)


@app.route('/api/system-stats')
def api_system_stats():
    """API endpoint untuk mendapatkan statistik sistem lengkap"""
    stats = rf_detector.get_detailed_stats()
    return jsonify(stats)


@app.route('/api/logs')
def api_logs():
    """API endpoint untuk mendapatkan login logs dari database SQLite"""
    logs = db.get_login_logs(limit=100)
    logs_data = []
    for log in logs:
        logs_data.append({
            'username': log[0],
            'success': log[1],
            'ip_address': log[2],
            'state': log[3],
            'message': log[4],
            'timestamp': log[5]
        })
    return jsonify(logs_data)


if __name__ == '__main__':
    # Berjalan di Port 5002 agar tidak tabrakan dengan FSA (5000) dan DT (5001)
    app.run(debug=True, host='0.0.0.0', port=5002)