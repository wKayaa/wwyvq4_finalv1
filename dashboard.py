#!/usr/bin/env python3
"""
🎨 K8s Exploit Master - Modern Dashboard Interface
Author: wKayaa
Date: 2025-06-23 23:07:45 UTC

Modern analytics dashboard inspired by DashTail design
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import asyncio
from datetime import datetime, timedelta
import os
from threading import Thread
import time
from k8s_exploit_master import K8sExploitMaster, ExploitationResult
import sqlite3
from dataclasses import asdict

app = Flask(__name__)

class DashboardManager:
    def __init__(self):
        self.db_path = 'dashboard_data.db'
        self.init_database()
        self.current_session = None
        self.exploit_master = None
        
    def init_database(self):
        """Initialize SQLite database for storing dashboard data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                status TEXT,
                targets_count INTEGER,
                clusters_scanned INTEGER,
                clusters_exploited INTEGER,
                credentials_found INTEGER,
                credentials_validated INTEGER
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
                credentials_count INTEGER,
                discovery_time TEXT,
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
        
        conn.commit()
        conn.close()
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard widgets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get totals
        cursor.execute('SELECT COUNT(*) FROM clusters')
        all_clusters = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM credentials WHERE validated = 1')
        validated_credentials = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clusters WHERE status = "exploited"')
        exploited_clusters = cursor.fetchone()[0]
        
        # Get recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE start_time > ?', (thirty_days_ago,))
        recent_sessions = cursor.fetchone()[0]
        
        # Get hourly activity for chart (last 24 hours)
        activity_data = []
        for i in range(24):
            hour_start = (datetime.now() - timedelta(hours=i+1)).isoformat()
            hour_end = (datetime.now() - timedelta(hours=i)).isoformat()
            cursor.execute('''
                SELECT COUNT(*) FROM credentials 
                WHERE extraction_time BETWEEN ? AND ?
            ''', (hour_start, hour_end))
            count = cursor.fetchone()[0]
            activity_data.append(count)
        
        activity_data.reverse()  # Chronological order
        
        # Get credential types breakdown
        cursor.execute('''
            SELECT type, COUNT(*) FROM credentials 
            WHERE validated = 1 
            GROUP BY type
        ''')
        credential_types = dict(cursor.fetchall())
        
        # Get top target countries (simulated data)
        countries_data = [
            {"name": "United States", "users": 28},
            {"name": "Germany", "users": 15},
            {"name": "United Kingdom", "users": 12},
            {"name": "France", "users": 8},
            {"name": "Canada", "users": 6}
        ]
        
        conn.close()
        
        return {
            'all_clusters': all_clusters,
            'validated_credentials': validated_credentials,
            'total_sessions': total_sessions,
            'exploited_clusters': exploited_clusters,
            'recent_sessions': recent_sessions,
            'activity_data': activity_data,
            'credential_types': credential_types,
            'countries_data': countries_data
        }
    
    def save_session_data(self, session_id, exploit_master, results):
        """Save session data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save session
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (id, start_time, end_time, status, targets_count, 
             clusters_scanned, clusters_exploited, credentials_found, credentials_validated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            exploit_master.start_time.isoformat(),
            datetime.now().isoformat(),
            'completed',
            len(results),
            exploit_master.stats['clusters_scanned'],
            exploit_master.stats['clusters_exploited'],
            exploit_master.stats['credentials_found'],
            exploit_master.stats['credentials_validated']
        ))
        
        # Save clusters and credentials
        for result in results:
            cursor.execute('''
                INSERT INTO clusters 
                (session_id, endpoint, status, vulnerable_pods, credentials_count, discovery_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                result.cluster_endpoint,
                result.status,
                len(result.vulnerable_pods),
                len(result.credentials_found),
                datetime.now().isoformat()
            ))
            
            for cred in result.credentials_found:
                cursor.execute('''
                    INSERT INTO credentials 
                    (session_id, cluster_endpoint, type, value, file_path, 
                     confidence, validated, validation_result, extraction_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    result.cluster_endpoint,
                    cred.type,
                    cred.value[:50] + '...' if len(cred.value) > 50 else cred.value,
                    cred.file_path,
                    cred.confidence,
                    cred.validated,
                    json.dumps(cred.validation_result),
                    cred.extraction_time
                ))
        
        conn.commit()
        conn.close()

# Global dashboard manager
dashboard_manager = DashboardManager()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = dashboard_manager.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    """API endpoint for real-time stats"""
    stats = dashboard_manager.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/start_exploitation', methods=['POST'])
def start_exploitation():
    """Start new exploitation session"""
    data = request.json
    targets = data.get('targets', [])
    telegram_token = data.get('telegram_token')
    telegram_chat_id = data.get('telegram_chat_id')
    discord_webhook = data.get('discord_webhook')
    
    if not targets:
        return jsonify({'error': 'No targets provided'}), 400
    
    # Start exploitation in background
    def run_exploitation():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        exploit_master = K8sExploitMaster(
            telegram_token=telegram_token,
            telegram_chat_id=telegram_chat_id,
            discord_webhook=discord_webhook
        )
        
        dashboard_manager.exploit_master = exploit_master
        
        try:
            results = loop.run_until_complete(
                exploit_master.run_mass_exploitation(targets)
            )
            dashboard_manager.save_session_data(
                exploit_master.session_id, exploit_master, results
            )
        except Exception as e:
            print(f"Exploitation error: {e}")
        finally:
            dashboard_manager.current_session = None
            dashboard_manager.exploit_master = None
    
    thread = Thread(target=run_exploitation)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'message': 'Exploitation started in background'})

@app.route('/api/session_status')
def session_status():
    """Get current session status"""
    if dashboard_manager.exploit_master:
        return jsonify({
            'active': True,
            'session_id': dashboard_manager.exploit_master.session_id,
            'stats': dashboard_manager.exploit_master.stats,
            'start_time': dashboard_manager.exploit_master.start_time.isoformat()
        })
    else:
        return jsonify({'active': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)