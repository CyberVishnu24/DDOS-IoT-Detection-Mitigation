# 🛡️ DDoS Attack Detection & Mitigation System - Complete Guide

## 🔴 PROBLEMS WITH YOUR ORIGINAL SETUP

1. **Port Mismatch**: 
   - Attacker targets port 8080
   - IoT server runs on port 5000
   - NGINX runs on default port 80
   - Result: **Attack never reaches your server!**

2. **No Mitigation**: You were only **detecting**, not **blocking** attacks

3. **Dashboard not monitoring actual traffic**: Wrong port configuration

---

## ✅ FIXED ARCHITECTURE

```
Attacker (attackerpro.py)
    ↓
Port 8080 (NGINX with Rate Limiting)
    ↓
Rate Limiting + Connection Control
    ↓
Port 5000 (Secured IoT Server)
    ↓
Application-level blocking
```

---

## 📦 FILES PROVIDED

| File | Purpose |
|------|---------|
| `nginx_ddos.conf` | NGINX configuration with DDoS protection |
| `iot_secured.py` | Enhanced IoT server with rate limiting |
| `monitor_advanced.py` | Network monitor with mitigation tracking |
| `dashboard_enhanced.py` | Real-time security dashboard |
| `setup.sh` | Automated setup script |

---

## 🚀 QUICK START

### Step 1: Setup
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Start Services (4 terminals)

**Terminal 1 - IoT Server:**
```bash
python3 iot_secured.py
```

**Terminal 2 - Network Monitor:**
```bash
python3 monitor_advanced.py
```

**Terminal 3 - Security Dashboard:**
```bash
python3 dashboard_enhanced.py
```
Then open: http://localhost:8050

**Terminal 4 - Run Attack (to test):**
```bash
python3 attackerpro.py
```

---

## 🔧 MITIGATION MECHANISMS

### 1. NGINX Layer (Port 8080)
- **Rate Limiting**: 10 requests/second per IP
- **Connection Limiting**: Max 10 concurrent connections per IP
- **Timeout Protection**: Prevents slowloris attacks
- **Buffer Limits**: Prevents memory exhaustion

### 2. Application Layer (Port 5000)
- **Dynamic IP Banning**: Blocks IPs exceeding 100 req/min
- **Ban Duration**: 5 minutes automatic unban
- **Connection Tracking**: Real-time per-IP monitoring
- **Graceful Degradation**: Legitimate users stay connected

### 3. Monitoring Layer
- **Real-time Traffic Analysis**: PPS, BPS tracking
- **SYN Flood Detection**: Tracks half-open connections
- **Mitigation Events Log**: Complete audit trail
- **System Resource Monitoring**: CPU, RAM tracking

---

## 📊 WHAT YOU'LL SEE DURING AN ATTACK

### Dashboard:
- 🚨 Status banner turns RED with "ATTACK DETECTED"
- 📈 PPS graph spikes dramatically
- 🔴 SYN connections increase
- ✅ "BLOCKED" counter increases (mitigation working!)
- 📝 Events log shows attack start/end

### IoT Server Console:
```
[ATTACK DETECTED] Banned 127.0.0.1 - 1847 req/min
[ATTACK DETECTED] Banned 127.0.0.1 - 2134 req/min
```

### Monitor Console:
```
[15:23:41] 🔴 UNDER ATTACK | PPS: 12847 | BLOCKED: 127
[15:23:42] 🔴 UNDER ATTACK | PPS: 11923 | BLOCKED: 134
[15:23:51] ✅ [ATTACK MITIGATED] Traffic normalized to 84 PPS
```

---

## 🧪 TESTING SCENARIOS

### Test 1: Normal Traffic (should pass)
```bash
# Send 5 requests (below rate limit)
for i in {1..5}; do curl http://localhost:8080; sleep 1; done
```
**Expected**: All requests succeed

### Test 2: Moderate Load (should trigger warning)
```bash
# Send 50 requests quickly
for i in {1..50}; do curl http://localhost:8080 & done
```
**Expected**: Some requests blocked, IP temporarily banned

### Test 3: Full DDoS Attack
```bash
python3 attackerpro.py
```
**Expected**: 
- Most traffic blocked at NGINX
- IP banned at application level
- Dashboard shows mitigation active

---

## 📈 DASHBOARD FEATURES

### Real-time Metrics:
1. **Network Traffic**: Live PPS graph with alert threshold
2. **System Resources**: CPU and RAM usage
3. **SYN Flood Detection**: Half-open connection tracking
4. **Mitigation Actions**: Blocked requests visualization
5. **Events Log**: Detailed timeline of attacks and mitigations

### Color Coding:
- 🟢 Green: System secure
- 🟡 Yellow: Elevated traffic
- 🔴 Red: Attack detected

---

## 🔐 NGINX CONFIGURATION EXPLAINED

```nginx
# Rate limiting: 10 requests/second per IP
limit_req_zone $binary_remote_addr zone=ddos_limit:10m rate=10r/s;

# Connection limiting: 10 concurrent per IP
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

# Burst allows temporary spikes (20 extra requests)
limit_req zone=ddos_limit burst=20 nodelay;
```

### Key Protections:
- **Slowloris Defense**: Short timeouts
- **Buffer Overflow Prevention**: Limited buffer sizes
- **Keep-Alive Abuse**: Short keepalive timeout
- **Suspicious Bot Blocking**: User-Agent filtering

---

## 🐛 TROUBLESHOOTING

### Issue: "Connection refused" when attacking
**Solution**: Check NGINX is running on port 8080
```bash
sudo netstat -tulpn | grep 8080
```

### Issue: "Permission denied" on log files
**Solution**: 
```bash
sudo chmod 644 /var/log/nginx/iot_*.log
```

### Issue: Dashboard not showing blocked requests
**Solution**: Monitor needs sudo access for connection stats
```bash
sudo python3 monitor_advanced.py
```

### Issue: NGINX test fails
**Solution**: Check configuration syntax
```bash
sudo nginx -t
```

---

## 📊 PERFORMANCE TUNING

### For Higher Traffic:
Edit `nginx_ddos.conf`:
```nginx
# Increase rate limit
limit_req_zone $binary_remote_addr zone=ddos_limit:10m rate=50r/s;

# Increase connections
limit_conn conn_limit 50;
```

### For More Aggressive Blocking:
Edit `iot_secured.py`:
```python
RATE_LIMIT = 50  # Lower = stricter
BAN_DURATION = 600  # Longer bans
```

---

## 📝 LOG FILES

| File | Content |
|------|---------|
| `traffic_fast.csv` | Real-time traffic metrics |
| `mitigation_events.csv` | Attack detection timeline |
| `/var/log/nginx/iot_access.log` | All NGINX requests |
| `/var/log/nginx/iot_error.log` | Rate limit violations |

---

## 🎯 SUCCESS CRITERIA

Your system is working correctly when:

✅ Dashboard shows real-time traffic  
✅ Attack causes PPS spike  
✅ "BLOCKED" counter increases during attack  
✅ Status banner turns red during attack  
✅ IoT server logs IP bans  
✅ Monitor shows "ATTACK DETECTED" and "ATTACK MITIGATED"  
✅ Events log records attack timeline  

---

## 🔬 UNDERSTANDING THE METRICS

### PPS (Packets Per Second)
- Normal: 10-100 PPS
- Warning: 500-1000 PPS
- Attack: 1000+ PPS

### SYN Connections
- Normal: 0-5
- Suspicious: 10-30
- Attack: 50+

### Blocked Requests
- During attack: Should be > 0
- If always 0: Mitigation not working

---

## 🚀 PRODUCTION RECOMMENDATIONS

1. **Use Hardware Firewall**: iptables/nftables for Layer 3/4 protection
2. **Implement GeoIP Blocking**: Block known malicious regions
3. **Add WAF**: Web Application Firewall (ModSecurity)
4. **Cloud DDoS Protection**: Cloudflare, AWS Shield
5. **Monitoring Alerts**: Email/SMS on attack detection
6. **Log Rotation**: Prevent disk space issues
7. **Load Balancing**: Distribute traffic across multiple servers

---

## 📚 ADDITIONAL RESOURCES

- NGINX Rate Limiting: https://www.nginx.com/blog/rate-limiting-nginx/
- iptables DDoS Protection: https://javapipe.com/blog/iptables-ddos-protection/
- OWASP DDoS Guide: https://owasp.org/www-community/attacks/Denial_of_Service

---

## ⚖️ LEGAL DISCLAIMER

This system is for **educational and testing purposes** on your own infrastructure only.

**DO NOT**:
- Attack systems you don't own
- Use in production without proper authorization
- Deploy without understanding security implications

**Unauthorized DDoS attacks are illegal in most jurisdictions.**

---

## 🆘 NEED HELP?

Common commands for debugging:

```bash
# Check NGINX status
sudo systemctl status nginx

# View real-time NGINX logs
sudo tail -f /var/log/nginx/iot_error.log

# Check active connections
sudo netstat -anp | grep :8080

# Monitor network traffic
sudo tcpdump -i lo port 8080

# Check iptables rules
sudo iptables -L -n -v
```

---

## 🎓 LEARNING OUTCOMES

By completing this project, you understand:

1. ✅ Multi-layer DDoS defense architecture
2. ✅ NGINX rate limiting and connection control
3. ✅ Application-level request filtering
4. ✅ Real-time traffic monitoring and analysis
5. ✅ Attack detection using statistical thresholds
6. ✅ Automated mitigation and IP blocking
7. ✅ Security dashboard development
8. ✅ System resource monitoring during attacks

---

**Built with ❤️ for IoT Security Research**
