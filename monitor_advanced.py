#!/usr/bin/env python3
"""
Advanced Network Monitor with Real-time Mitigation Tracking
"""
import psutil
import time
import csv
import os
from collections import defaultdict
import subprocess

INTERFACE = "lo"
LOG_FILE = "traffic_fast.csv"
PORT = 8080
ALERT_THRESHOLD_PPS = 1000
MITIGATION_LOG = "mitigation_events.csv"

# Connection tracking
connection_tracker = defaultdict(int)

def get_connection_stats():
    """Get detailed connection statistics"""
    syn_count = 0
    established = 0
    time_wait = 0
    close_wait = 0
    
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.laddr and conn.laddr.port == PORT:
                if conn.status == 'SYN_RECV':
                    syn_count += 1
                elif conn.status == 'ESTABLISHED':
                    established += 1
                elif conn.status == 'TIME_WAIT':
                    time_wait += 1
                elif conn.status == 'CLOSE_WAIT':
                    close_wait += 1
    except:
        pass
    
    return syn_count, established, time_wait, close_wait

def check_nginx_rate_limit():
    """Check NGINX error log for rate limiting events"""
    blocked = 0
    try:
        result = subprocess.run(
            ['sudo', 'tail', '-n', '100', '/var/log/nginx/iot_error.log'],
            capture_output=True,
            text=True,
            timeout=1
        )
        blocked = result.stdout.count('limiting requests')
    except:
        pass
    return blocked

# Initialize CSV files
with open(LOG_FILE, "w", newline="") as f:
    csv.writer(f).writerow(["timestamp", "pps", "bps", "syn", "established", "blocked"])

with open(MITIGATION_LOG, "w", newline="") as f:
    csv.writer(f).writerow(["timestamp", "event_type", "details", "action_taken"])

prev = psutil.net_io_counters(pernic=True)[INTERFACE]
attack_active = False

print("=" * 70)
print("🔍 ADVANCED NETWORK MONITOR WITH MITIGATION TRACKING")
print("=" * 70)
print(f"Target Port: {PORT}")
print(f"Alert Threshold: {ALERT_THRESHOLD_PPS} PPS")
print(f"Interface: {INTERFACE}")
print("-" * 70)

try:
    while True:
        time.sleep(1)
        
        # Get network counters
        now = psutil.net_io_counters(pernic=True)[INTERFACE]
        packets = (now.packets_recv + now.packets_sent) - (prev.packets_recv + prev.packets_sent)
        bytes_ = (now.bytes_recv + now.bytes_sent) - (prev.bytes_recv + prev.bytes_sent)
        prev = now
        
        pps = packets
        bps = bytes_
        
        # Get connection stats
        syn, established, time_wait, close_wait = get_connection_stats()
        
        # Check NGINX blocking
        blocked = check_nginx_rate_limit()
        
        # Detect attack
        current_time = time.strftime('%H:%M:%S')
        
        if pps > ALERT_THRESHOLD_PPS and not attack_active:
            attack_active = True
            print(f"\n🚨 [ATTACK DETECTED] {current_time}")
            print(f"   PPS: {pps} | SYN: {syn} | Established: {established}")
            
            with open(MITIGATION_LOG, "a", newline="") as f:
                csv.writer(f).writerow([
                    current_time,
                    "ATTACK_START",
                    f"PPS:{pps},SYN:{syn}",
                    "NGINX_RATE_LIMITING_ACTIVE"
                ])
        
        elif pps < ALERT_THRESHOLD_PPS * 0.5 and attack_active:
            attack_active = False
            print(f"\n✅ [ATTACK MITIGATED] {current_time}")
            print(f"   Traffic normalized to {pps} PPS")
            
            with open(MITIGATION_LOG, "a", newline="") as f:
                csv.writer(f).writerow([
                    current_time,
                    "ATTACK_END",
                    f"Final_PPS:{pps}",
                    "TRAFFIC_NORMALIZED"
                ])
        
        # Log to CSV
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([current_time, pps, bps, syn, established, blocked])
        
        # Console output
        status = "🔴 UNDER ATTACK" if attack_active else "🟢 NORMAL"
        print(f"[{current_time}] {status} | PPS: {pps:>5} | BPS: {bps:>8} | SYN: {syn:>3} | EST: {established:>3} | BLOCKED: {blocked:>3}")

except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("📊 MONITORING SESSION ENDED")
    print("=" * 70)
    print(f"Logs saved to: {LOG_FILE}")
    print(f"Mitigation events: {MITIGATION_LOG}")
