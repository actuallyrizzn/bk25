# 🚀 BK25 v1.0.0 - Production Deployment Guide

**Status**: ✅ **SHIPPED**  
**Version**: 1.0.0  
**Date**: December 2024

---

## 🎯 **Production Ready**

BK25 v1.0.0 is **officially shipped** and ready for production deployment. This guide covers all aspects of deploying BK25 in production environments.

---

## 🏗️ **System Requirements**

### **Minimum Requirements**
- **OS**: Linux (Ubuntu 20.04+), macOS 11+, or Windows 10+
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM (1GB recommended)
- **Storage**: 100MB disk space
- **Network**: Internet access for LLM APIs

### **Recommended Requirements**
- **OS**: Ubuntu 22.04 LTS or CentOS 8+
- **Python**: 3.11 or higher
- **Memory**: 2GB RAM
- **Storage**: 500MB disk space
- **CPU**: 2+ cores
- **Network**: Stable internet connection

---

## 🚀 **Quick Deployment**

### **1. Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/your-org/bk25.git
cd bk25

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Key Configuration Variables:**
```env
# Server Configuration
HOST=0.0.0.0
PORT=3003
DEBUG=false

# LLM Configuration
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3003"]

# Logging
LOG_LEVEL=info
LOG_FILE=logs/bk25.log
```

### **3. Start Production Server**
```bash
# Using Gunicorn (recommended for production)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3003

# Or using Uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 3003 --workers 4
```

---

## 🐳 **Docker Deployment**

### **1. Build Docker Image**
```bash
# Build the image
docker build -t bk25:1.0.0 .

# Or use docker-compose
docker-compose up -d --build
```

### **2. Docker Compose (Recommended)**
```yaml
# docker-compose.yml
version: '3.8'
services:
  bk25:
    build: .
    ports:
      - "3003:3003"
    environment:
      - HOST=0.0.0.0
      - PORT=3003
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **3. Run with Docker**
```bash
# Start the service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bk25
```

---

## ☁️ **Cloud Deployment**

### **AWS EC2**
```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Clone and setup BK25
git clone https://github.com/your-org/bk25.git
cd bk25
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/bk25.service
```

**Systemd Service Configuration:**
```ini
[Unit]
Description=BK25 AI Automation Service
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/bk25
Environment=PATH=/home/ubuntu/bk25/venv/bin
ExecStart=/home/ubuntu/bk25/venv/bin/gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3003
Restart=always

[Install]
WantedBy=multi-user.target
```

### **Google Cloud Run**
```bash
# Deploy to Cloud Run
gcloud run deploy bk25 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3003
```

### **Azure App Service**
```bash
# Deploy to Azure App Service
az webapp up --name bk25 --resource-group myResourceGroup --runtime "PYTHON:3.11"
```

---

## 🔧 **Production Configuration**

### **1. Environment Variables**
```bash
# Production environment file
PRODUCTION=true
DEBUG=false
LOG_LEVEL=info
SECRET_KEY=your-very-secure-secret-key
CORS_ORIGINS=["https://yourdomain.com"]
```

### **2. Reverse Proxy (Nginx)**
```nginx
# /etc/nginx/sites-available/bk25
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **3. SSL/HTTPS (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **Monitoring & Health Checks**

### **1. Health Check Endpoint**
```bash
# Check service health
curl http://localhost:3003/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-12-01T12:00:00Z",
  "version": "1.0.0"
}
```

### **2. System Monitoring**
```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor application logs
tail -f logs/bk25.log

# Check service status
systemctl status bk25
```

### **3. Log Rotation**
```bash
# Setup logrotate
sudo nano /etc/logrotate.d/bk25
```

**Logrotate Configuration:**
```
/home/ubuntu/bk25/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
```

---

## 🔒 **Security Configuration**

### **1. Firewall Setup**
```bash
# Configure UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### **2. API Security**
```bash
# Rate limiting configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS configuration
CORS_ORIGINS=["https://yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true
```

### **3. Environment Security**
```bash
# Secure environment file
chmod 600 .env
chown ubuntu:ubuntu .env

# Secure application directory
chmod 755 /home/ubuntu/bk25
chown -R ubuntu:ubuntu /home/ubuntu/bk25
```

---

## 📈 **Scaling & Performance**

### **1. Load Balancing**
```nginx
# Nginx upstream configuration
upstream bk25_backend {
    server 127.0.0.1:3003;
    server 127.0.0.1:3004;
    server 127.0.0.1:3005;
}

server {
    location / {
        proxy_pass http://bk25_backend;
    }
}
```

### **2. Process Management**
```bash
# Increase worker processes
gunicorn src.main:app -w 8 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3003

# Or use multiple instances
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:3003 &
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:3004 &
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:3005 &
```

### **3. Performance Tuning**
```bash
# System tuning
echo 'net.core.somaxconn = 65535' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Service Won't Start**
```bash
# Check logs
journalctl -u bk25 -f

# Check configuration
python -c "import src.main; print('Import successful')"

# Check dependencies
pip list | grep fastapi
```

#### **2. Performance Issues**
```bash
# Monitor resources
top -p $(pgrep -f gunicorn)

# Check network
netstat -tulpn | grep :3003

# Check disk I/O
iostat -x 1
```

#### **3. Connection Issues**
```bash
# Test local connectivity
curl http://localhost:3003/health

# Check firewall
sudo ufw status

# Check nginx
sudo nginx -t
sudo systemctl status nginx
```

---

## 📋 **Deployment Checklist**

### **Pre-Deployment**
- [ ] System requirements met
- [ ] Dependencies installed
- [ ] Environment configured
- [ ] SSL certificates obtained
- [ ] Firewall configured

### **Deployment**
- [ ] Application deployed
- [ ] Service started
- [ ] Health checks passing
- [ ] Reverse proxy configured
- [ ] SSL/HTTPS working

### **Post-Deployment**
- [ ] Monitoring configured
- [ ] Logs being generated
- [ ] Performance acceptable
- [ ] Security measures active
- [ ] Backup strategy implemented

---

## 🎉 **Success!**

Once you've completed the deployment checklist, BK25 v1.0.0 will be running in production! 

### **Verify Deployment**
```bash
# Check service status
curl https://yourdomain.com/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-12-01T12:00:00Z",
  "version": "1.0.0"
}
```

### **Access Your Application**
- **Web Interface**: https://yourdomain.com
- **API Documentation**: https://yourdomain.com/docs
- **Health Status**: https://yourdomain.com/health

---

## 📞 **Support**

- **Documentation**: [Project Wiki](https://github.com/your-org/bk25/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/bk25/issues)
- **Community**: [GitHub Discussions](https://github.com/your-org/bk25/discussions)

---

**BK25 v1.0.0 is SHIPPED and ready for production!** 🚀

*Generate enterprise automation without enterprise complexity.* 🤖✨
