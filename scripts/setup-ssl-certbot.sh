#!/bin/bash

# SSL Certificate Setup Script using Let's Encrypt (Certbot)
# This script sets up SSL certificates for cmeetrading.com
# Usage: ./scripts/setup-ssl-certbot.sh [email]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN="cmeetrading.com"
EMAIL="${1:-admin@cmeetrading.com}"
CERTBOT_DIR="/etc/letsencrypt"
WEBROOT="/var/www/certbot"
NGINX_DIR="/root/forexxx/nginx"

echo -e "${BLUE}=========================================="
echo "SSL Certificate Setup - Let's Encrypt"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "==========================================${NC}\n"

# Function to print step
print_step() {
    echo -e "\n${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}\n"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

print_step "Step 1: Prerequisites Check"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}✗ Please run as root (use sudo)${NC}"
    exit 1
fi
check_success "Running as root"

# Check if domain DNS is configured
echo -e "${YELLOW}Checking DNS configuration...${NC}"
if dig +short $DOMAIN | grep -q .; then
    check_success "DNS record found for $DOMAIN"
    echo -e "${YELLOW}DNS IP: $(dig +short $DOMAIN | head -1)${NC}"
else
    echo -e "${RED}✗ DNS record not found for $DOMAIN${NC}"
    echo -e "${YELLOW}Please configure DNS A record pointing to this server before continuing${NC}"
    exit 1
fi

# Check if ports 80 and 443 are accessible
echo -e "${YELLOW}Checking port accessibility...${NC}"
if netstat -tuln | grep -q ":80 "; then
    check_success "Port 80 is open"
else
    echo -e "${YELLOW}⚠ Port 80 is not open - ensure firewall allows HTTP traffic${NC}"
fi

if netstat -tuln | grep -q ":443 "; then
    check_success "Port 443 is open"
else
    echo -e "${YELLOW}⚠ Port 443 is not open - ensure firewall allows HTTPS traffic${NC}"
fi

print_step "Step 2: Install Certbot"

# Check if certbot is installed
if command -v certbot &> /dev/null; then
    check_success "Certbot already installed"
    certbot --version
else
    echo -e "${YELLOW}Installing certbot...${NC}"
    
    # Detect OS
    if [ -f /etc/debian_version ]; then
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
        check_success "Certbot installed (Debian/Ubuntu)"
    elif [ -f /etc/redhat-release ]; then
        yum install -y certbot python3-certbot-nginx
        check_success "Certbot installed (RHEL/CentOS)"
    else
        echo -e "${RED}✗ Unsupported OS. Please install certbot manually${NC}"
        exit 1
    fi
fi

print_step "Step 3: Create Required Directories"

# Create directories for certbot webroot
mkdir -p "$WEBROOT"
mkdir -p "$NGINX_DIR/certbot/conf"
mkdir -p "$NGINX_DIR/certbot/www"
chmod -R 755 "$NGINX_DIR/certbot"

check_success "Directories created"

print_step "Step 4: Stop Nginx (if running)"

# Stop nginx if running to allow certbot to use port 80
if docker ps | grep -q "digital_utopia_nginx_proxy"; then
    echo -e "${YELLOW}Stopping nginx container...${NC}"
    docker stop digital_utopia_nginx_proxy || true
    check_success "Nginx container stopped"
else
    check_success "Nginx container not running"
fi

print_step "Step 5: Request SSL Certificate"

# Check if certificate already exists
if [ -d "$CERTBOT_DIR/live/$DOMAIN" ]; then
    echo -e "${YELLOW}Certificate already exists for $DOMAIN${NC}"
    read -p "Do you want to renew it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        certbot renew --dry-run
        check_success "Certificate renewal test"
    else
        echo -e "${GREEN}✓ Using existing certificate${NC}"
    fi
else
    echo -e "${YELLOW}Requesting new certificate for $DOMAIN...${NC}"
    
    # Request certificate using standalone mode (nginx is stopped)
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --preferred-challenges http
    
    check_success "Certificate obtained for $DOMAIN"
fi

# Verify certificate files
if [ -f "$CERTBOT_DIR/live/$DOMAIN/fullchain.pem" ] && \
   [ -f "$CERTBOT_DIR/live/$DOMAIN/privkey.pem" ]; then
    check_success "Certificate files verified"
    echo -e "${GREEN}Certificate location: $CERTBOT_DIR/live/$DOMAIN/${NC}"
else
    echo -e "${RED}✗ Certificate files not found${NC}"
    exit 1
fi

print_step "Step 6: Setup Auto-Renewal"

# Create renewal hook script
cat > /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh << 'EOF'
#!/bin/bash
# Reload nginx after certificate renewal
docker restart digital_utopia_nginx_proxy || true
EOF

chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh
check_success "Renewal hook script created"

# Test renewal
echo -e "${YELLOW}Testing certificate renewal...${NC}"
certbot renew --dry-run
check_success "Certificate renewal test passed"

# Setup cron job for auto-renewal (runs twice daily)
CRON_JOB="0 0,12 * * * certbot renew --quiet --deploy-hook /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh"
(crontab -l 2>/dev/null | grep -v "certbot renew" || true; echo "$CRON_JOB") | crontab -
check_success "Auto-renewal cron job configured"

print_step "Step 7: Verify Certificate"

# Display certificate information
echo -e "${YELLOW}Certificate Information:${NC}"
openssl x509 -in "$CERTBOT_DIR/live/$DOMAIN/fullchain.pem" -noout -subject -dates 2>/dev/null || true

# Check certificate expiration
EXPIRY_DATE=$(openssl x509 -in "$CERTBOT_DIR/live/$DOMAIN/fullchain.pem" -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -n "$EXPIRY_DATE" ]; then
    echo -e "${GREEN}Certificate expires: $EXPIRY_DATE${NC}"
fi

print_step "Step 8: Next Steps"

echo -e "${GREEN}=========================================="
echo "SSL Certificate Setup Complete!"
echo "==========================================${NC}\n"

echo -e "${YELLOW}Important Notes:${NC}"
echo "1. Certificate files are located at: $CERTBOT_DIR/live/$DOMAIN/"
echo "2. Auto-renewal is configured to run twice daily"
echo "3. Nginx configuration is already set up to use these certificates"
echo "4. Start nginx container: docker-compose up -d nginx-proxy"
echo "5. Test SSL: openssl s_client -connect $DOMAIN:443 -servername $DOMAIN"
echo ""
echo -e "${YELLOW}To verify SSL:${NC}"
echo "  curl -I https://$DOMAIN"
echo "  openssl s_client -connect $DOMAIN:443 -servername $DOMAIN"
echo ""
echo -e "${YELLOW}To manually renew certificate:${NC}"
echo "  certbot renew"
echo ""
echo -e "${GREEN}✓ Setup complete!${NC}\n"

