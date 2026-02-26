# 📦 Installation Guide

Complete installation instructions for the IoT DDoS Defense System.

---

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows 10/11
- **Python**: 3.8 or higher (3.9+ recommended)
- **RAM**: Minimum 512MB, Recommended 1GB
- **Disk Space**: 200MB for installation + logs
- **Network**: Ports 8080, 8081, 8050 available

### Check Python Version

```bash
python3 --version
# Should show: Python 3.8.x or higher
```

If Python 3.8+ is not installed:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

**macOS (using Homebrew):**
```bash
brew install python@3.9
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

---

## 🚀 Quick Installation (Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/iot-ddos-defense.git
cd iot-ddos-defense
```

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

**Standard Installation:**
```bash
pip install -r requirements.txt
```

**Minimal Installation (dashboard only):**
```bash
pip install -r requirements-minimal.txt
```

**Exact Versions (reproducible):**
```bash
pip install -r requirements-freeze.txt
```

**Development Setup:**
```bash
pip install -r requirements-dev.txt
```

### Step 4: Verify Installation

```bash
python3 -c "import dash, pandas, psutil, plotly; print('✓ All dependencies installed successfully')"
```

Expected output:
```
✓ All dependencies installed successfully
```

---

## 🔧 Manual Installation

If automatic installation fails, install packages individually:

```bash
# Core dependencies
pip install dash==2.14.2
pip install plotly==5.18.0
pip install pandas==2.1.4
pip install psutil==5.9.6
```

---

## 🐳 Docker Installation (Alternative)

### Using Docker Compose (Recommended)

**Step 1: Create `docker-compose.yml`**

```yaml
version: '3.8'

services:
  iot-backend:
    build: .
    container_name: iot-backend
    ports:
      - "8080:8080"
    command: python3 iot_secured1.py
    restart: unless-stopped

  mitigation-proxy:
    build: .
    container_name: mitigation-proxy
    ports:
      - "8081:8081"
    depends_on:
      - iot-backend
    command: python3 pro_mitigator.py
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  dashboard:
    build: .
    container_name: dashboard
    ports:
      - "8050:8050"
    depends_on:
      - mitigation-proxy
    command: python3 dashboard_enhanced.py
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

**Step 2: Create `Dockerfile`**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Expose ports
EXPOSE 8080 8081 8050

# Default command (overridden by docker-compose)
CMD ["python3", "pro_mitigator.py"]
```

**Step 3: Build and Run**

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Step 4: Access Services**

- Dashboard: http://localhost:8050
- Proxy: http://localhost:8081
- Backend: http://localhost:8080 (internal)

---

## 🛠️ Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev build-essential

# Clone and setup
git clone https://github.com/yourusername/iot-ddos-defense.git
cd iot-ddos-defense
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### CentOS/RHEL/Fedora

```bash
# Install system dependencies
sudo yum install -y python3-pip python3-devel gcc

# Clone and setup
git clone https://github.com/yourusername/iot-ddos-defense.git
cd iot-ddos-defense
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### macOS

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9

# Clone and setup
git clone https://github.com/yourusername/iot-ddos-defense.git
cd iot-ddos-defense
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows

**Using pip:**

```cmd
:: Clone repository
git clone https://github.com/yourusername/iot-ddos-defense.git
cd iot-ddos-defense

:: Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

:: Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Using Anaconda:**

```cmd
:: Create conda environment
conda create -n ddos-defense python=3.9
conda activate ddos-defense

:: Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Testing Installation

### Test 1: Import Test

```bash
python3 << EOF
import sys
print(f"Python version: {sys.version}")

try:
    import dash
    print(f"✓ Dash {dash.__version__}")
except ImportError:
    print("✗ Dash not installed")

try:
    import plotly
    print(f"✓ Plotly {plotly.__version__}")
except ImportError:
    print("✗ Plotly not installed")

try:
    import pandas
    print(f"✓ Pandas {pandas.__version__}")
except ImportError:
    print("✗ Pandas not installed")

try:
    import psutil
    print(f"✓ Psutil {psutil.__version__}")
except ImportError:
    print("✗ Psutil not installed")
EOF
```

Expected output:
```
Python version: 3.9.x
✓ Dash 2.14.2
✓ Plotly 5.18.0
✓ Pandas 2.1.4
✓ Psutil 5.9.6
```

### Test 2: Port Availability

```bash
# Check if ports are available
netstat -tuln | grep -E '8080|8081|8050'

# Should return empty (no output = ports free)
```

### Test 3: Run Quick Test

```bash
# Start backend in background
python3 iot_secured1.py &
PID_BACKEND=$!

# Wait for startup
sleep 2

# Test connection
curl -s http://127.0.0.1:8080/ | python3 -m json.tool

# Expected output:
# {
#     "device": "IoT Sensor",
#     "status": "secure",
#     ...
# }

# Cleanup
kill $PID_BACKEND
```

---

## ❌ Troubleshooting

### Error: `ModuleNotFoundError: No module named 'dash'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows

# Reinstall
pip install dash
```

### Error: `Permission denied` when binding to ports

**Solution (Linux/macOS):**
```bash
# Option 1: Use ports >1024 (recommended)
# Edit configuration files to use 8080, 8081, 8050

# Option 2: Run with sudo (not recommended)
sudo python3 pro_mitigator.py
```

### Error: `pip: command not found`

**Solution:**
```bash
# Install pip
python3 -m ensurepip --upgrade

# Or use package manager
sudo apt install python3-pip  # Ubuntu/Debian
brew install python3           # macOS
```

### Error: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
```bash
# Install certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Or disable SSL verification (not recommended)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Error: `Building wheel for X failed`

**Solution:**
```bash
# Install build tools

# Ubuntu/Debian
sudo apt install python3-dev build-essential

# CentOS/RHEL
sudo yum install python3-devel gcc

# macOS
xcode-select --install

# Windows
# Install "Microsoft C++ Build Tools" from visualstudio.microsoft.com
```

---

## 🔄 Updating

### Update Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade dash plotly pandas psutil
```

### Update from Git

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies (in case requirements changed)
pip install -r requirements.txt
```

---

## 🗑️ Uninstallation

### Remove Virtual Environment

```bash
# Deactivate environment
deactivate

# Remove virtual environment folder
rm -rf venv

# Remove project files
cd ..
rm -rf iot-ddos-defense
```

### Remove System-wide Installation

```bash
# If installed globally (not recommended)
pip uninstall dash plotly pandas psutil
```

---

## 📞 Getting Help

If installation fails:

1. **Check Python version**: `python3 --version` (must be 3.8+)
2. **Check pip version**: `pip --version` (should be 20.0+)
3. **Try minimal install**: `pip install -r requirements-minimal.txt`
4. **Check error logs**: Look for specific error messages
5. **Search issues**: [GitHub Issues](https://github.com/yourusername/iot-ddos-defense/issues)
6. **Ask for help**: Create a new issue with:
   - Python version
   - Operating system
   - Full error message
   - Output of `pip list`

---

## ✅ Next Steps

After successful installation:

1. **Read the main README**: [README.md](README.md)
2. **Run Quick Start**: Follow terminal setup in README
3. **Test with simulator**: Run `attackerpro.py` (change port to 8081)
4. **View dashboard**: Open http://localhost:8050
5. **Configure for production**: See [Security Considerations](README.md#-security-considerations)

---

**Installation complete! 🎉**
