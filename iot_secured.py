#!/usr/bin/env python3
"""
Enhanced IoT Server with Built-in DDoS Detection
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import defaultdict
import time
import threading
import json

# Configuration
PORT = 5000
RATE_LIMIT = 100  # Max requests per IP per minute
BAN_DURATION = 300  # Ban for 5 minutes

# Tracking dictionaries
request_tracker = defaultdict(list)
banned_ips = {}
stats = {"total_requests": 0, "blocked_requests": 0, "active_connections": 0}

def cleanup_old_requests():
    """Remove requests older than 60 seconds"""
    while True:
        time.sleep(10)
        current_time = time.time()
        for ip in list(request_tracker.keys()):
            request_tracker[ip] = [
                t for t in request_tracker[ip] 
                if current_time - t < 60
            ]
            if not request_tracker[ip]:
                del request_tracker[ip]
        
        # Remove expired bans
        for ip in list(banned_ips.keys()):
            if current_time > banned_ips[ip]:
                del banned_ips[ip]
                print(f"[UNBAN] {ip}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_requests, daemon=True)
cleanup_thread.start()

class IoTHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        client_ip = self.client_address[0]
        current_time = time.time()
        
        stats["total_requests"] += 1
        
        # Check if IP is banned
        if client_ip in banned_ips:
            if current_time < banned_ips[client_ip]:
                stats["blocked_requests"] += 1
                self.send_error(429, "Too Many Requests - Temporarily Banned")
                return
            else:
                del banned_ips[client_ip]
        
        # Track request
        request_tracker[client_ip].append(current_time)
        
        # Check rate limit
        if len(request_tracker[client_ip]) > RATE_LIMIT:
            banned_ips[client_ip] = current_time + BAN_DURATION
            stats["blocked_requests"] += 1
            print(f"[ATTACK DETECTED] Banned {client_ip} - {len(request_tracker[client_ip])} req/min")
            self.send_error(429, "Rate Limit Exceeded")
            return
        
        # Normal response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        response = {
            "status": "active",
            "device": "IoT Sensor",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "your_ip": client_ip,
            "requests_last_min": len(request_tracker[client_ip])
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.do_GET()

if __name__ == '__main__':
    server = HTTPServer(("127.0.0.1", PORT), IoTHandler)
    print("=" * 60)
    print(f"🛡️  SECURED IoT SERVER RUNNING ON PORT {PORT}")
    print("=" * 60)
    print(f"Rate Limit: {RATE_LIMIT} requests/min per IP")
    print(f"Ban Duration: {BAN_DURATION} seconds")
    print("Press Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n📊 FINAL STATISTICS:")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Blocked Requests: {stats['blocked_requests']}")
        print(f"Blocked IPs: {len(banned_ips)}")
        print("\nServer stopped.")
