#!/usr/bin/env node
/**
 * Staging Deployment Script
 * Automates deployment to staging environment
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

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

function checkPrerequisites() {
  logSection('Checking Prerequisites');

  const checks = [
    { name: 'Node.js', command: 'node --version' },
    { name: 'npm', command: 'npm --version' },
  ];

  let allPassed = true;
  checks.forEach(check => {
    try {
      const version = execSync(check.command, { encoding: 'utf-8' }).trim();
      log(`✅ ${check.name}: ${version}`, 'green');
    } catch (error) {
      log(`❌ ${check.name}: Not found`, 'red');
      allPassed = false;
    }
  });

  // Check for .env.staging
  const envFile = path.join(rootDir, '.env.staging');
  if (!fs.existsSync(envFile)) {
    log(`⚠️  .env.staging not found. Using default environment variables.`, 'yellow');
  } else {
    log(`✅ .env.staging found`, 'green');
  }

  return allPassed;
}

function buildApplication() {
  logSection('Building Application');

  // Install dependencies if needed
  if (!fs.existsSync(path.join(rootDir, 'node_modules'))) {
    if (!execCommand('npm ci', 'Installing dependencies')) {
      return false;
    }
  }

  // Build for production
  if (!execCommand('npm run build', 'Building application')) {
    return false;
  }

  // Verify build output
  const distDir = path.join(rootDir, 'dist');
  if (!fs.existsSync(distDir)) {
    log('❌ Build output directory not found', 'red');
    return false;
  }

  const files = fs.readdirSync(distDir);
  if (files.length === 0) {
    log('❌ Build output is empty', 'red');
    return false;
  }

  log(`✅ Build output verified (${files.length} files)`, 'green');
  return true;
}

function generateDeploymentInfo() {
  logSection('Generating Deployment Info');

  const info = {
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || 'unknown',
    gitCommit: getGitCommit(),
    buildTime: new Date().toISOString(),
    environment: 'staging',
  };

  const infoPath = path.join(rootDir, 'dist', 'deployment-info.json');
  fs.writeFileSync(infoPath, JSON.stringify(info, null, 2));
  log(`✅ Deployment info generated: ${infoPath}`, 'green');

  return info;
}

function getGitCommit() {
  try {
    return execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
  } catch {
    return 'unknown';
  }
}

function verifyBuild() {
  logSection('Verifying Build');

  const distDir = path.join(rootDir, 'dist');
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
    log(`✅ Assets directory found (${assets.length} files)`, 'green');
  }

  return allFound;
}

function main() {
  log('\n🚀 Staging Deployment Script', 'cyan');
  log(`Working directory: ${rootDir}\n`, 'blue');

  // Step 1: Check prerequisites
  if (!checkPrerequisites()) {
    log('\n❌ Prerequisites check failed. Please fix issues and try again.', 'red');
    process.exit(1);
  }

  // Step 2: Build application
  if (!buildApplication()) {
    log('\n❌ Build failed. Please fix build errors and try again.', 'red');
    process.exit(1);
  }

  // Step 3: Generate deployment info
  const deploymentInfo = generateDeploymentInfo();

  // Step 4: Verify build
  if (!verifyBuild()) {
    log('\n❌ Build verification failed.', 'red');
    process.exit(1);
  }

  // Step 5: Summary
  logSection('Deployment Summary');
  log(`✅ Build completed successfully`, 'green');
  log(`📦 Build output: ${path.join(rootDir, 'dist')}`, 'blue');
  log(`📝 Deployment info:`, 'blue');
  console.log(JSON.stringify(deploymentInfo, null, 2));

  log('\n✨ Staging build ready for deployment!', 'green');
  log('\nNext steps:', 'cyan');
  log('1. Copy dist/ contents to staging server', 'blue');
  log('2. Configure nginx/server for staging', 'blue');
  log('3. Run smoke tests on staging', 'blue');
  log('4. Verify all routes work correctly', 'blue');
  log('5. Check error logs', 'blue');
}

main();


