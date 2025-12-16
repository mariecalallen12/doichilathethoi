# Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the client application to production.

## Pre-Deployment Checklist

### Code & Testing

- [ ] All tests passing
- [ ] Code review completed
- [ ] Security review passed
- [ ] Performance review passed
- [ ] UAT sign-off obtained
- [ ] Documentation updated

### Environment

- [ ] Production environment provisioned
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] CDN configured (if applicable)

### Infrastructure

- [ ] Server resources adequate
- [ ] Database configured
- [ ] Backup system ready
- [ ] Monitoring configured
- [ ] Alerts configured

### Backup & Rollback

- [ ] Current production backed up
- [ ] Database backup taken
- [ ] Rollback procedure tested
- [ ] Previous version tagged
- [ ] Rollback scripts ready

## Deployment Steps

### Step 1: Pre-Deployment

```bash
# 1. Final code review
git log --oneline -10

# 2. Create release tag
git tag -a v2.0.0 -m "Production release v2.0.0"
git push origin v2.0.0

# 3. Backup current production (if exists)
# - Database backup
# - File system backup
# - Configuration backup
```

### Step 2: Build Production Bundle

```bash
# Navigate to client-app directory
cd /root/forexxx/client-app

# Install dependencies (if needed)
npm ci --production=false

# Build for production
npm run build

# Verify build output
ls -lh dist/

# Check bundle sizes
du -sh dist/*
```

### Step 3: Deploy to Staging First

```bash
# Deploy to staging environment
# This allows final verification before production

# 1. Copy build files to staging server
scp -r dist/* staging-server:/var/www/client-app/

# 2. Verify staging deployment
# - Check all routes work
# - Verify API connections
# - Test critical features
# - Check error logs
```

### Step 4: Staging Verification

**Smoke Tests:**
- [ ] Homepage loads
- [ ] Login works
- [ ] Education page loads
- [ ] Analysis page loads
- [ ] Support pages load
- [ ] Legal pages load
- [ ] API connections work
- [ ] WebSocket connects

**Performance Check:**
- [ ] Page load times acceptable
- [ ] No console errors
- [ ] No network errors
- [ ] Bundle sizes reasonable

### Step 5: Production Deployment

#### Option A: Direct Deployment

```bash
# 1. Enable maintenance mode (if applicable)
# 2. Copy build files to production server
scp -r dist/* production-server:/var/www/client-app/

# 3. Restart web server
ssh production-server "sudo systemctl restart nginx"

# 4. Disable maintenance mode
# 5. Verify deployment
```

#### Option B: Docker Deployment

```bash
# 1. Build Docker image
docker build -t client-app:v2.0.0 .

# 2. Tag for production
docker tag client-app:v2.0.0 registry.example.com/client-app:v2.0.0

# 3. Push to registry
docker push registry.example.com/client-app:v2.0.0

# 4. Deploy to production
# (Using your orchestration tool: Kubernetes, Docker Swarm, etc.)
kubectl set image deployment/client-app client-app=registry.example.com/client-app:v2.0.0

# 5. Verify deployment
kubectl rollout status deployment/client-app
```

#### Option C: CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
# .github/workflows/deploy-production.yml

name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - name: Deploy to production
        # Add deployment steps
```

### Step 6: Post-Deployment Verification

**Immediate Checks (First 5 minutes):**

```bash
# 1. Check server status
curl -I https://your-domain.com

# 2. Check API connectivity
curl https://api.production.com/api/health

# 3. Check error logs
tail -f /var/log/nginx/error.log

# 4. Check application logs
tail -f /var/log/client-app/app.log
```

**Functional Verification:**

- [ ] Homepage accessible
- [ ] All routes work
- [ ] API endpoints respond
- [ ] WebSocket connects
- [ ] Authentication works
- [ ] No console errors
- [ ] No 404 errors
- [ ] No 500 errors

**Performance Verification:**

- [ ] Page load times < 3s
- [ ] API response times < 500ms
- [ ] No memory leaks
- [ ] No CPU spikes

### Step 7: Monitoring

**First Hour:**
- Monitor error rates
- Monitor response times
- Check user reports
- Watch error tracking (Sentry)
- Monitor server resources

**First Day:**
- Review error logs
- Check performance metrics
- Collect user feedback
- Monitor for issues

**First Week:**
- Daily monitoring
- Performance analysis
- User feedback review
- Issue resolution

## Rollback Procedure

### When to Rollback

- Critical bugs affecting users
- Performance degradation
- Security issues
- Data corruption
- High error rates

### Rollback Steps

```bash
# 1. Enable maintenance mode
# 2. Restore previous version

# Option A: Git-based rollback
git checkout <previous-tag>
npm run build
# Deploy previous build

# Option B: Docker rollback
kubectl rollout undo deployment/client-app

# Option C: File system restore
# Restore from backup

# 3. Verify rollback
# 4. Disable maintenance mode
# 5. Notify team
```

## Deployment Verification Checklist

### Functional

- [ ] All pages load correctly
- [ ] Navigation works
- [ ] Forms submit correctly
- [ ] API calls succeed
- [ ] WebSocket connects
- [ ] Authentication works
- [ ] Data displays correctly

### Performance

- [ ] Page load < 3s
- [ ] API response < 500ms
- [ ] No memory leaks
- [ ] Bundle sizes acceptable
- [ ] Images optimized

### Security

- [ ] HTTPS enabled
- [ ] Security headers set
- [ ] No exposed secrets
- [ ] CORS configured correctly
- [ ] Authentication secure

### Monitoring

- [ ] Error tracking working
- [ ] Performance monitoring active
- [ ] Alerts configured
- [ ] Logs accessible
- [ ] Dashboards updated

## Post-Deployment Tasks

### Immediate (First Hour)

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify critical features
- [ ] Respond to any issues
- [ ] Update status page

### Short-term (First Day)

- [ ] Review error logs
- [ ] Analyze performance data
- [ ] Collect user feedback
- [ ] Document any issues
- [ ] Plan fixes if needed

### Medium-term (First Week)

- [ ] Performance optimization
- [ ] Bug fixes
- [ ] User feedback implementation
- [ ] Documentation updates
- [ ] Team retrospective

## Communication

### Pre-Deployment

- Notify stakeholders
- Schedule maintenance window (if needed)
- Brief support team
- Prepare status updates

### During Deployment

- Real-time status updates
- Issue notifications
- Progress reports

### Post-Deployment

- Deployment success notification
- Known issues communication
- Performance summary
- Next steps

## Troubleshooting

### Common Issues

**Build Fails:**
- Check Node.js version
- Verify dependencies
- Check for syntax errors
- Review build logs

**Deployment Fails:**
- Check server permissions
- Verify disk space
- Check network connectivity
- Review deployment logs

**Application Errors:**
- Check error logs
- Verify environment variables
- Check API connectivity
- Review recent changes

**Performance Issues:**
- Check server resources
- Review database queries
- Analyze bundle sizes
- Check CDN configuration

## Success Criteria

- ✅ Deployment successful
- ✅ All features working
- ✅ Performance acceptable
- ✅ No critical errors
- ✅ Monitoring active
- ✅ Team notified
- ✅ Documentation updated

## Notes

- Always deploy to staging first
- Test rollback procedure regularly
- Keep deployment logs
- Document any issues
- Learn from each deployment
- Improve process continuously

