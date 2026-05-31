from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from fsa_detector import FSADetector, State
from database import Database
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'


# Inisialisasi FSA Detector dan Database
fsa_detector = FSADetector(max_attempts=5, time_window=60, block_duration=300)
db = Database()


@app.route('/')
def index():
    """Halaman utama - redirect ke login"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login - HYBRID TRACKING (Username + IP)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        ip_address = request.remote_addr
        
        # Verifikasi credentials DULU
        is_valid = db.verify_credentials(username, password)
        
        # Record login attempt dengan HYBRID tracking (username + IP)
        result = fsa_detector.record_login_attempt(username, ip_address, is_valid)
        
        # Log ke database
        db.log_login_attempt(username, is_valid, ip_address,
                            result['state'].value, result['message'])
        
        # Handle berdasarkan hasil
        if is_valid and result['state'] != State.BLOCKED:
            # Login berhasil dan tidak diblokir
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        elif result['state'] == State.BLOCKED:
            # Diblokir (username atau IP)
            return render_template('blocked.html',
                                 blocked_until=result.get('blocked_until'),
                                 message=result['message'],
                                 reason=result.get('reason'))
        
        else:
            # Login gagal (NORMAL atau SUSPICIOUS)
            return render_template('login.html',
                                 error=result['message'],
                                 state=result['state'].value,
                                 failed_attempts=result.get('failed_attempts', 0),
                                 remaining_attempts=result.get('remaining_attempts', 0),
                                 reason=result.get('reason'),
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
    
    # Get statistics untuk username dan IP
    stats = fsa_detector.get_statistics(username=username, ip_address=ip_address)
    detailed_stats = fsa_detector.get_detailed_stats()
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
    """API endpoint untuk mendapatkan statistik user"""
    ip_address = request.remote_addr
    stats = fsa_detector.get_statistics(username=username, ip_address=ip_address)
    return jsonify(stats)


@app.route('/api/system-stats')
def api_system_stats():
    """API endpoint untuk mendapatkan statistik sistem lengkap"""
    stats = fsa_detector.get_detailed_stats()
    return jsonify(stats)


@app.route('/api/logs')
def api_logs():
    """API endpoint untuk mendapatkan login logs"""
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
    app.run(debug=True, host='0.0.0.0', port=5000)
