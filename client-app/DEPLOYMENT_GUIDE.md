# Production Deployment Guide - Client App

**Version**: 1.0  
**Last Updated**: 2025-01-08

---

## Overview

This guide provides step-by-step instructions for deploying the client application to production.

---

## Prerequisites

- Docker 20.x or higher
- Docker Compose 2.x or higher
- Access to production server
- Production API URL and WebSocket URL
- SSL/TLS certificates (for HTTPS)

---

## Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Production API URL confirmed
- [ ] Production WebSocket URL confirmed
- [ ] SSL certificates ready (if using HTTPS)
- [ ] Backend API is deployed and accessible
- [ ] Database migrations completed
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Health checks configured

---

## Deployment Methods

### Method 1: Docker Compose (Recommended)

#### Step 1: Prepare Environment Variables

Create or update `.env` file in project root:

```env
# Client App Environment Variables
CLIENT_API_BASE_URL=https://api.yourdomain.com
CLIENT_WS_URL=wss://api.yourdomain.com/ws
CLIENT_PORT=3002
```

#### Step 2: Build and Deploy

```bash
# Build and start services
docker-compose up -d client-app

# Or use production override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d client-app
```

#### Step 3: Verify Deployment

```bash
# Check container status
docker ps | grep client-app

# Check logs
docker logs digital_utopia_client

# Test health endpoint
curl http://localhost:3002/health
```

#### Step 4: Test Application

1. Open browser: `http://your-server:3002`
2. Test navigation links
3. Test login flow
4. Verify API calls work
5. Check browser console for errors

---

### Method 2: Docker Build and Run

#### Step 1: Build Production Image

```bash
cd client-app

docker build \
  --build-arg VITE_API_BASE_URL=https://api.yourdomain.com \
  --build-arg VITE_WS_URL=wss://api.yourdomain.com/ws \
  -t client-app:latest .
```

#### Step 2: Run Container

```bash
docker run -d \
  --name client-app \
  -p 3002:80 \
  --restart unless-stopped \
  client-app:latest
```

#### Step 3: Verify

```bash
# Check container
docker ps | grep client-app

# Check logs
docker logs client-app

# Test
curl http://localhost:3002
```

---

### Method 3: Manual Build and Deploy

#### Step 1: Build Application

```bash
cd client-app

# Create .env file
cat > .env << EOF
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
EOF

# Install dependencies
npm install --legacy-peer-deps

# Build for production
npm run build
```

#### Step 2: Deploy Build Output

The build output is in `dist/` directory. Deploy this to your web server:

```bash
# Copy to web server
scp -r dist/* user@server:/var/www/client-app/

# Or use rsync
rsync -avz dist/ user@server:/var/www/client-app/
```

#### Step 3: Configure Web Server

**Nginx Configuration**:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/client-app;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

## Environment Variables Configuration

### Development

Create `.env` file in `client-app/`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### Production (Docker)

Set via build arguments:

```bash
docker build \
  --build-arg VITE_API_BASE_URL=https://api.yourdomain.com \
  --build-arg VITE_WS_URL=wss://api.yourdomain.com/ws \
  -t client-app:latest .
```

Or via docker-compose:

```yaml
services:
  client-app:
    build:
      args:
        VITE_API_BASE_URL: ${CLIENT_API_BASE_URL}
        VITE_WS_URL: ${CLIENT_WS_URL}
```

### Production (Manual Build)

Set in `.env` before building:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
```

**Important**: Environment variables are replaced at build time. You must rebuild after changing them.

---

## SSL/TLS Configuration

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:3002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Using Docker with SSL

```yaml
services:
  nginx-proxy:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
```

---

## Health Checks

### Docker Health Check

The Dockerfile includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/health || exit 1
```

### Manual Health Check

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' client-app

# Test health endpoint
curl http://localhost:3002/health
```

### Nginx Health Endpoint

Add to nginx configuration:

```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

---

## Monitoring

### Log Monitoring

```bash
# View logs
docker logs -f client-app

# View last 100 lines
docker logs --tail 100 client-app

# View logs with timestamps
docker logs -t client-app
```

### Application Monitoring

Monitor the following:
- Container status
- API response times
- Error rates
- WebSocket connections
- User sessions

### Performance Monitoring

- Page load times
- API call performance
- WebSocket latency
- Resource usage (CPU, memory)

---

## Troubleshooting Deployment

### Container Won't Start

```bash
# Check logs
docker logs client-app

# Check container status
docker ps -a | grep client-app

# Restart container
docker restart client-app
```

### API Calls Failing

1. Verify `VITE_API_BASE_URL` is set correctly
2. Check CORS configuration on backend
3. Verify backend is accessible
4. Check network connectivity

```bash
# Test API connectivity
curl https://api.yourdomain.com/api/health

# Check environment variables in container
docker exec client-app printenv | grep VITE
```

### WebSocket Connection Failing

1. Verify `VITE_WS_URL` is set correctly
2. Check WebSocket server is running
3. Verify SSL certificates (for wss://)
4. Check firewall rules

```bash
# Test WebSocket connection
wscat -c wss://api.yourdomain.com/ws
```

### Environment Variables Not Working

1. Verify variables start with `VITE_` prefix
2. Rebuild after changing variables
3. Check Docker build args
4. Verify variables in container

```bash
# Check build args were used
docker inspect client-app | grep -A 10 Env

# Rebuild with correct args
docker build --build-arg VITE_API_BASE_URL=... client-app
```

---

## Rollback Procedure

### Docker Compose

```bash
# Stop current version
docker-compose stop client-app

# Rollback to previous image
docker tag client-app:previous client-app:latest
docker-compose up -d client-app
```

### Docker

```bash
# Stop container
docker stop client-app

# Remove container
docker rm client-app

# Run previous version
docker run -d --name client-app -p 3002:80 client-app:previous
```

### Manual Deployment

```bash
# Restore previous build
cd /var/www/client-app
rm -rf dist
cp -r dist.backup dist
```

---

## Backup Strategy

### Build Artifacts

```bash
# Backup dist folder
tar -czf client-app-backup-$(date +%Y%m%d).tar.gz dist/

# Backup Docker image
docker save client-app:latest | gzip > client-app-image-$(date +%Y%m%d).tar.gz
```

### Configuration

```bash
# Backup environment files
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

---

## Post-Deployment Verification

### Checklist

- [ ] Application accessible at production URL
- [ ] Navigation links work correctly
- [ ] Login flow works correctly
- [ ] API calls succeed
- [ ] WebSocket connections work
- [ ] No errors in browser console
- [ ] No errors in server logs
- [ ] Health checks passing
- [ ] Performance is acceptable
- [ ] SSL/TLS working (if applicable)

### Testing Commands

```bash
# Test API integration
node scripts/test-production-api.mjs \
  --api-url=https://api.yourdomain.com \
  --ws-url=wss://api.yourdomain.com/ws

# Test health endpoint
curl https://yourdomain.com/health

# Test WebSocket
wscat -c wss://api.yourdomain.com/ws
```

---

## Maintenance

### Regular Updates

1. Pull latest code
2. Update dependencies: `npm install --legacy-peer-deps`
3. Rebuild: `npm run build`
4. Deploy new build
5. Verify deployment

### Monitoring

- Check logs daily
- Monitor error rates
- Review performance metrics
- Check user feedback

---

## Support

For deployment issues:
1. Check [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)
2. Review container logs
3. Verify environment variables
4. Test API connectivity
5. Contact development team

---

**Last Updated**: 2025-01-08

