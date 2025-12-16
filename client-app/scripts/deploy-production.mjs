#!/usr/bin/env node
/**
 * Production Deployment Script
 * Automates deployment to production environment with safety checks
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  console.log('\n' + '='.repeat(60));
  log(title, 'cyan');
  console.log('='.repeat(60));
}

function execCommand(command, description) {
  try {
    log(`\n${description}...`, 'blue');
    execSync(command, { stdio: 'inherit', cwd: rootDir });
    log(`✅ ${description} completed`, 'green');
    return true;
  } catch (error) {
    log(`❌ ${description} failed: ${error.message}`, 'red');
    return false;
  }
}

function askQuestion(query) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise(resolve => {
    rl.question(query, answer => {
      rl.close();
      resolve(answer);
    });
  });
}

async function confirmProductionDeployment() {
  logSection('Production Deployment Confirmation');
  
  log('⚠️  WARNING: This will deploy to PRODUCTION!', 'yellow');
  log('Please confirm the following:', 'cyan');
  
  const checks = [
    'All tests are passing',
    'Code review completed',
    'Security review passed',
    'UAT sign-off obtained',
    'Backup of current production taken',
    'Rollback plan prepared',
    'Stakeholders notified',
  ];

  checks.forEach((check, index) => {
    log(`${index + 1}. ${check}`, 'blue');
  });

  const answer = await askQuestion('\nHave you completed all checks? (yes/no): ');
  
  if (answer.toLowerCase() !== 'yes') {
    log('\n❌ Deployment cancelled. Please complete all checks first.', 'red');
    return false;
  }

  const finalConfirm = await askQuestion('\nType "DEPLOY" to confirm production deployment: ');
  
  if (finalConfirm !== 'DEPLOY') {
    log('\n❌ Deployment cancelled. Confirmation not received.', 'red');
    return false;
  }

  return true;
}

function checkProductionPrerequisites() {
  logSection('Checking Production Prerequisites');

  // Check for .env.production
  const envFile = path.join(rootDir, '.env.production');
  if (!fs.existsSync(envFile)) {
    log('❌ .env.production not found', 'red');
    log('   Please create .env.production with production environment variables', 'yellow');
    return false;
  }
  log('✅ .env.production found', 'green');

  // Check for production API URL
  const envContent = fs.readFileSync(envFile, 'utf-8');
  if (!envContent.includes('VITE_API_BASE_URL=https://')) {
    log('⚠️  Warning: VITE_API_BASE_URL may not be set to production URL', 'yellow');
  }

  // Verify tests pass
  log('\nRunning tests...', 'blue');
  if (!execCommand('npm run test -- --run', 'Running tests')) {
    log('❌ Tests failed. Cannot deploy to production.', 'red');
    return false;
  }

  return true;
}

function createProductionBuild() {
  logSection('Creating Production Build');

  // Set production environment
  process.env.NODE_ENV = 'production';
  process.env.VITE_APP_ENV = 'production';

  // Install dependencies
  if (!execCommand('npm ci --production=false', 'Installing dependencies')) {
    return false;
  }

  // Build for production
  if (!execCommand('npm run build', 'Building for production')) {
    return false;
  }

  return true;
}

function createReleaseTag() {
  logSection('Creating Release Tag');

  const version = process.env.npm_package_version || 'unknown';
  const gitCommit = getGitCommit();
  const tagName = `v${version}-${gitCommit}`;

  try {
    execSync(`git tag -a ${tagName} -m "Production release ${tagName}"`, { cwd: rootDir });
    log(`✅ Release tag created: ${tagName}`, 'green');
    return tagName;
  } catch (error) {
    log(`⚠️  Could not create git tag: ${error.message}`, 'yellow');
    return null;
  }
}

function getGitCommit() {
  try {
    return execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
  } catch {
    return 'unknown';
  }
}

function generateProductionInfo() {
  logSection('Generating Production Deployment Info');

  const info = {
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || 'unknown',
    gitCommit: getGitCommit(),
    buildTime: new Date().toISOString(),
    environment: 'production',
    deployedBy: process.env.USER || 'unknown',
  };

  const infoPath = path.join(rootDir, 'dist', 'deployment-info.json');
  fs.writeFileSync(infoPath, JSON.stringify(info, null, 2));
  log(`✅ Deployment info generated: ${infoPath}`, 'green');

  return info;
}

function verifyProductionBuild() {
  logSection('Verifying Production Build');

  const distDir = path.join(rootDir, 'dist');
  
  // Check required files
  const requiredFiles = ['index.html'];
  let allFound = true;
  
  requiredFiles.forEach(file => {
    const filePath = path.join(distDir, file);
    if (fs.existsSync(filePath)) {
      log(`✅ ${file} found`, 'green');
    } else {
      log(`❌ ${file} not found`, 'red');
      allFound = false;
    }
  });

  // Check bundle sizes
  const assetsDir = path.join(distDir, 'assets');
  if (fs.existsSync(assetsDir)) {
    const assets = fs.readdirSync(assetsDir);
    let totalSize = 0;
    
    assets.forEach(asset => {
      const assetPath = path.join(assetsDir, asset);
      const stats = fs.statSync(assetPath);
      totalSize += stats.size;
    });

    const totalSizeMB = (totalSize / 1024 / 1024).toFixed(2);
    log(`✅ Total bundle size: ${totalSizeMB} MB`, 'green');
    
    if (totalSize > 5 * 1024 * 1024) { // 5MB
      log(`⚠️  Warning: Bundle size is large (${totalSizeMB} MB)`, 'yellow');
    }
  }

  return allFound;
}

async function main() {
  log('\n🚀 Production Deployment Script', 'cyan');
  log(`Working directory: ${rootDir}\n`, 'blue');

  // Step 1: Confirm deployment
  if (!(await confirmProductionDeployment())) {
    process.exit(1);
  }

  // Step 2: Check prerequisites
  if (!checkProductionPrerequisites()) {
    log('\n❌ Prerequisites check failed. Please fix issues and try again.', 'red');
    process.exit(1);
  }

  // Step 3: Create production build
  if (!createProductionBuild()) {
    log('\n❌ Production build failed. Please fix errors and try again.', 'red');
    process.exit(1);
  }

  // Step 4: Create release tag
  const releaseTag = createReleaseTag();

  // Step 5: Generate deployment info
  const deploymentInfo = generateProductionInfo();

  // Step 6: Verify build
  if (!verifyProductionBuild()) {
    log('\n❌ Build verification failed.', 'red');
    process.exit(1);
  }

  // Step 7: Final summary
  logSection('Production Deployment Summary');
  log(`✅ Production build completed successfully`, 'green');
  log(`📦 Build output: ${path.join(rootDir, 'dist')}`, 'blue');
  if (releaseTag) {
    log(`🏷️  Release tag: ${releaseTag}`, 'blue');
  }
  log(`📝 Deployment info:`, 'blue');
  console.log(JSON.stringify(deploymentInfo, null, 2));

  log('\n✨ Production build ready for deployment!', 'green');
  log('\n⚠️  IMPORTANT: Before deploying:', 'yellow');
  log('1. Verify build on staging first', 'blue');
  log('2. Backup current production', 'blue');
  log('3. Copy dist/ contents to production server', 'blue');
  log('4. Configure nginx/server for production', 'blue');
  log('5. Run smoke tests immediately after deployment', 'blue');
  log('6. Monitor error logs and performance', 'blue');
  log('7. Have rollback plan ready', 'blue');
}

main().catch(error => {
  log(`\n❌ Fatal error: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});


