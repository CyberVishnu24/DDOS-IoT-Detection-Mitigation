#!/bin/bash
# DDoS Mitigation Setup Script

echo "==============================================="
echo "🛡️  IoT DDoS Detection & Mitigation Setup"
echo "==============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Install dependencies
echo -e "\n${YELLOW}[1/6]${NC} Installing Python dependencies..."
pip install dash plotly pandas psutil --break-system-packages

# Step 2: Configure NGINX
echo -e "\n${YELLOW}[2/6]${NC} Configuring NGINX..."
sudo cp nginx_ddos.conf /etc/nginx/sites-available/iot-ddos
sudo ln -sf /etc/nginx/sites-available/iot-ddos /etc/nginx/sites-enabled/
sudo nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ NGINX configuration valid${NC}"
    sudo systemctl reload nginx
else
    echo -e "${RED}✗ NGINX configuration error${NC}"
    exit 1
fi

# Step 3: Create log directory
echo -e "\n${YELLOW}[3/6]${NC} Setting up log directories..."
sudo mkdir -p /var/log/nginx
sudo touch /var/log/nginx/iot_access.log /var/log/nginx/iot_error.log
sudo chown -R www-data:www-data /var/log/nginx

# Step 4: Make scripts executable
echo -e "\n${YELLOW}[4/6]${NC} Making scripts executable..."
chmod +x iot_secured.py monitor_advanced.py dashboard_enhanced.py

# Step 5: Create systemd services (optional)
echo -e "\n${YELLOW}[5/6]${NC} Would you like to create systemd services? (y/n)"
read -r create_services

if [ "$create_services" = "y" ]; then
    cat > /tmp/iot-server.service << EOF
[Unit]
Description=Secured IoT Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) $(pwd)/iot_secured.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    cat > /tmp/iot-monitor.service << EOF
[Unit]
Description=IoT Network Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) $(pwd)/monitor_advanced.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    cat > /tmp/iot-dashboard.service << EOF
[Unit]
Description=IoT Security Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) $(pwd)/dashboard_enhanced.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/iot-*.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo -e "${GREEN}✓ Systemd services created${NC}"
fi

# Step 6: Summary
echo -e "\n${GREEN}==============================================="
echo "✅ Setup Complete!"
echo "===============================================${NC}"
echo ""
echo "To start the system manually:"
echo ""
echo "  Terminal 1: python3 iot_secured.py"
echo "  Terminal 2: python3 monitor_advanced.py"
echo "  Terminal 3: python3 dashboard_enhanced.py"
echo "  Terminal 4: python3 attackerpro.py  (to test)"
echo ""
echo "Access dashboard: http://localhost:8050"
echo ""
echo "If you created systemd services:"
echo "  sudo systemctl start iot-server"
echo "  sudo systemctl start iot-monitor"
echo "  sudo systemctl start iot-dashboard"
echo ""
echo "Architecture:"
echo "  Attacker → Port 8080 (NGINX) → Rate Limiting → Port 5000 (IoT Server)"
echo ""
