
from flask import Flask, jsonify, render_template, request
import threading
import logging
import os
import sys

# Suppress Flask CLI banner
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

class WebDashboard:
    def __init__(self, app_controller):
        self.app_controller = app_controller # Reference to GameClaimerApp
        
        # Determine template folder relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, 'templates')
        
        self.server = Flask(__name__, template_folder=template_dir)
        self.server.add_url_rule('/', 'index', self.index)
        self.server.add_url_rule('/api/status', 'status', self.api_status)
        self.server.add_url_rule('/api/start', 'start', self.api_start, methods=['POST'])
        self.server.add_url_rule('/api/stop', 'stop', self.api_stop, methods=['POST'])
        
        # Disable Flask logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def run(self, port=5000):
        try:
            # host='0.0.0.0' allows access from local network
            self.server.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Web Dashboard Error: {e}")

    def index(self):
        return render_template('index.html')

    def api_status(self):
        # Gather status from App Controller
        dashboard = self.app_controller.frames.get("dashboard")
        
        status_text = "Stopped"
        is_running = False
        next_claim = "Unknown"
        logs = []
        
        if dashboard:
            is_running = getattr(dashboard, "is_running", False)
            status_text = "Running" if is_running else "Stopped"
            
            # Helper to get next claim time if available
            # This depends on how dashboard exposes this data
            # For now returning placeholder
            
            # Fetch recent logs from history
            from src.utils.claimed_history import ClaimedHistory
            history = ClaimedHistory() # Re-instantiate to read latest from disk? Or use dashboard's instance?
            # Better to use dashboard's instance if possible to avoid file contention
            # but reading is fine.
            logs = history.get_recent_logs()[:10] # Top 10
            
        return jsonify({
            "status": status_text,
            "running": is_running,
            "logs": logs
        })

    def api_start(self):
        dashboard = self.app_controller.frames.get("dashboard")
        if dashboard and not dashboard.is_running:
            # Trigger start via thread to avoid blocking
            dashboard.toggle_claim() 
            return jsonify({"success": True, "message": "Started"})
        return jsonify({"success": False, "message": "Already running or not ready"})

    def api_stop(self):
        dashboard = self.app_controller.frames.get("dashboard")
        if dashboard and dashboard.is_running:
            dashboard.toggle_claim()
            return jsonify({"success": True, "message": "Stopped"})
        return jsonify({"success": False, "message": "Already stopped"})
