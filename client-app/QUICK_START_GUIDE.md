# Quick Start Guide

**Version**: 2.0.0  
**Last Updated**: 2025-01-12

## For Developers

### Initial Setup

```bash
# Install dependencies
npm install --legacy-peer-deps

# Create environment file
cp ENV_EXAMPLE.md .env
# Edit .env with your configuration

# Start development server
npm run dev
```

### Running Tests

```bash
# Run all tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## For Content Team

### Content Population

1. **Review Templates**
   ```bash
   # Generate content templates
   node scripts/generate-content-templates.mjs
   
   # Review generated templates
   cat CONTENT_TEMPLATES.md
   ```

2. **Use Templates**
   - JSON templates are in `content-templates/` directory
   - Use as starting points for content creation
   - Validate content before submission

3. **Content Types**
   - Education: Videos, Ebooks, Calendar Events, Reports
   - Support: Articles, FAQ, Office Locations, Channels
   - Legal: Terms, Privacy Policy, Risk Warning

## For QA/UAT Team

### UAT Execution

1. **Generate UAT Files**
   ```bash
   node scripts/uat-helper.mjs
   ```

2. **Use Checklists**
   - Review `UAT_CHECKLIST.md`
   - Execute test scenarios
   - Document findings

3. **Report Results**
   - Use `UAT_REPORT_TEMPLATE.md`
   - Document all issues
   - Provide recommendations

## For DevOps

### Staging Deployment

```bash
# Run staging deployment script
node scripts/deploy-staging.mjs
```

### Production Deployment

```bash
# Run production deployment script
node scripts/deploy-production.mjs
```

### Backend Verification

```bash
# Verify backend endpoints
node scripts/verify-backend-endpoints.mjs

# With custom API URL
API_BASE_URL=http://your-api-url node scripts/verify-backend-endpoints.mjs
```

## Common Tasks

### Check API Health
```javascript
import { checkApiHealth } from './src/utils/apiHealthCheck';

const health = await checkApiHealth();
console.log(health);
```

### Validate Content
```javascript
import { validateContent } from './src/utils/contentValidator';

const result = validateContent('video', videoData);
if (!result.valid) {
  console.error('Errors:', result.errors);
}
```

### Monitor Performance
```javascript
import { reportPerformanceMetrics } from './src/utils/performanceMonitor';

const metrics = reportPerformanceMetrics();
console.log(metrics);
```

## Troubleshooting

### Build Errors
- Check `TROUBLESHOOTING_GUIDE.md`
- Verify all imports are correct
- Check environment variables

### Test Failures
- Run tests individually to isolate issues
- Check test setup in `vitest.config.js`
- Verify mocks are properly configured

### API Connection Issues
- Verify `VITE_API_BASE_URL` in `.env`
- Check backend server is running
- Review `BACKEND_ENDPOINTS_VERIFICATION.md`

## Documentation Index

- **Getting Started**: `README.md`
- **Deployment**: `DEPLOYMENT_GUIDE.md`
- **Content**: `CONTENT_POPULATION_GUIDE.md`
- **UAT**: `UAT_EXECUTION_GUIDE.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`
- **Status**: `COMPREHENSIVE_IMPLEMENTATION_STATUS.md`

## Support

For issues or questions:
1. Check relevant documentation
2. Review troubleshooting guide
3. Check existing issues
4. Contact development team

---

**Quick Reference**: All scripts are in `scripts/` directory, all documentation is in root directory.


