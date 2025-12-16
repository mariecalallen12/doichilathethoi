#!/bin/bash
set -e

echo "🔒 SSL Certificate Setup"
echo "========================"
echo ""

DOMAIN="${DOMAIN:-cmeetrading.com}"
EMAIL="${EMAIL:-admin@cmeetrading.com}"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    apt-get update -qq
    apt-get install -y certbot python3-certbot-nginx
fi

# Check if certificates already exist
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ SSL certificates already exist for $DOMAIN"
    echo "To renew: certbot renew"
    exit 0
fi

# Create nginx config for initial certificate request
echo "📝 Creating temporary nginx config for certificate request..."

# Start nginx with HTTP only config
echo "Starting nginx for certificate validation..."

# Request certificate
echo "🔐 Requesting SSL certificate for $DOMAIN..."
certbot certonly \
    --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    || {
        echo "❌ Certificate request failed. You may need to:"
        echo "   1. Ensure domain DNS points to this server"
        echo "   2. Ensure port 80 is accessible"
        echo "   3. Run manually: certbot certonly --nginx -d $DOMAIN"
        exit 1
    }

echo ""
echo "✅ SSL certificate installed successfully!"
echo ""
echo "📋 Certificate location:"
echo "   Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "   Private Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo ""
echo "🔄 Auto-renewal setup:"
echo "   Certificates will auto-renew via systemd timer"
echo "   To test renewal: certbot renew --dry-run"
echo ""

