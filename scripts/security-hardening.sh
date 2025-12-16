#!/bin/bash
set -e

echo "🔒 Security Hardening"
echo "===================="
echo ""

# Check and update .env file
echo "🔐 Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "✅ .env file created. Please update with production values!"
fi

# Check for default passwords
echo "🔍 Checking for default passwords..."
if grep -q "CHANGE.*PASSWORD\|CHANGE.*SECRET" .env 2>/dev/null; then
    echo "⚠️  WARNING: Default passwords/keys found in .env file!"
    echo "   Please update: POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY"
fi

# Generate strong SECRET_KEY if needed
if grep -q "CHANGE-THIS.*SECRET" .env 2>/dev/null; then
    echo "🔑 Generating new SECRET_KEY..."
    NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET/" .env
    echo "✅ SECRET_KEY generated and updated"
fi

# Check Docker security
echo "🐳 Checking Docker security..."
echo "   - Ensure containers run as non-root user"
echo "   - Verify resource limits are set"
echo "   - Check network isolation"

# Check firewall
echo "🔥 Checking firewall..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "✅ UFW firewall is active"
    else
        echo "⚠️  UFW firewall is not active. Consider enabling it:"
        echo "   sudo ufw enable"
        echo "   sudo ufw allow 22/tcp"
        echo "   sudo ufw allow 80/tcp"
        echo "   sudo ufw allow 443/tcp"
    fi
fi

# Check SSL/TLS
echo "🔐 Checking SSL/TLS configuration..."
if [ -f "/etc/letsencrypt/live/cmeetrading.com/fullchain.pem" ]; then
    echo "✅ SSL certificates found"
    
    # Check certificate expiry
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/cmeetrading.com/fullchain.pem 2>/dev/null | cut -d= -f2)
    if [ -n "$EXPIRY" ]; then
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
        
        if [ $DAYS_LEFT -lt 30 ]; then
            echo "⚠️  SSL certificate expires in $DAYS_LEFT days"
        else
            echo "✅ SSL certificate valid for $DAYS_LEFT more days"
        fi
    fi
else
    echo "⚠️  SSL certificates not found. Run: ./scripts/setup-ssl.sh"
fi

# Check rate limiting in nginx
echo "🚦 Checking rate limiting..."
if grep -q "limit_req_zone" nginx/nginx.prod.conf 2>/dev/null; then
    echo "✅ Rate limiting configured in nginx"
else
    echo "⚠️  Rate limiting not found in nginx config"
fi

# Check security headers
echo "🛡️  Checking security headers..."
if grep -q "Strict-Transport-Security\|X-Frame-Options\|X-Content-Type-Options" nginx/nginx.prod.conf 2>/dev/null; then
    echo "✅ Security headers configured"
else
    echo "⚠️  Security headers not found in nginx config"
fi

# Check database access
echo "🗄️  Checking database access..."
if docker ps --format '{{.Names}}' | grep -q "digital_utopia_postgres"; then
    # Check if postgres port is exposed
    if docker port digital_utopia_postgres 2>/dev/null | grep -q "5432"; then
        echo "⚠️  WARNING: PostgreSQL port is exposed to host!"
        echo "   In production, remove port mapping from docker-compose.yml"
    else
        echo "✅ PostgreSQL port not exposed (good for security)"
    fi
fi

# Check Redis access
if docker ps --format '{{.Names}}' | grep -q "digital_utopia_redis"; then
    if docker port digital_utopia_redis 2>/dev/null | grep -q "6379"; then
        echo "⚠️  WARNING: Redis port is exposed to host!"
        echo "   In production, remove port mapping and require password"
    else
        echo "✅ Redis port not exposed (good for security)"
    fi
fi

echo ""
echo "✅ Security hardening check completed!"
echo ""
echo "📋 Security Checklist:"
echo "   [ ] Update all default passwords in .env"
echo "   [ ] Enable firewall (UFW)"
echo "   [ ] Setup SSL certificates"
echo "   [ ] Remove exposed database ports in production"
echo "   [ ] Enable Redis password authentication"
echo "   [ ] Review and restrict CORS origins"
echo "   [ ] Setup regular security updates"
echo ""

