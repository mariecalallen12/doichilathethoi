import { readFileSync } from 'fs';
import { validateContent } from '../src/utils/contentValidator.js';

let allValid = true;
let errors = [];
let warnings = [];

console.log('Starting content validation...\n');

// Validate articles
try {
  const articles = JSON.parse(readFileSync('content-templates/support/articles.json', 'utf8'));
  console.log(`Validating ${articles.length} articles...`);
  articles.forEach((article, idx) => {
    const result = validateContent('article', article);
    if (!result.valid) {
      allValid = false;
      errors.push(`Article ${idx + 1} (${article.title}): ${result.errors.join(', ')}`);
    }
    if (result.warnings.length > 0) {
      warnings.push(`Article ${idx + 1} (${article.title}): ${result.warnings.join(', ')}`);
    }
  });
  console.log(`✓ Articles validated: ${articles.length} items\n`);
} catch (err) {
  console.error('Error validating articles:', err.message);
  allValid = false;
}

// Validate FAQ
try {
  const faqs = JSON.parse(readFileSync('content-templates/support/faq.json', 'utf8'));
  console.log(`Validating ${faqs.length} FAQ items...`);
  faqs.forEach((faq, idx) => {
    const result = validateContent('faq', faq);
    if (!result.valid) {
      allValid = false;
      errors.push(`FAQ ${idx + 1}: ${result.errors.join(', ')}`);
    }
    if (result.warnings.length > 0) {
      warnings.push(`FAQ ${idx + 1}: ${result.warnings.join(', ')}`);
    }
  });
  console.log(`✓ FAQs validated: ${faqs.length} items\n`);
} catch (err) {
  console.error('Error validating FAQs:', err.message);
  allValid = false;
}

// Validate Terms of Service
try {
  const terms = JSON.parse(readFileSync('content-templates/legal/terms.json', 'utf8'));
  console.log('Validating Terms of Service...');
  const termsResult = validateContent('terms-of-service', terms);
  if (!termsResult.valid) {
    allValid = false;
    errors.push(`Terms of Service: ${termsResult.errors.join(', ')}`);
  }
  if (termsResult.warnings.length > 0) {
    warnings.push(`Terms of Service: ${termsResult.warnings.join(', ')}`);
  }
  console.log('✓ Terms of Service validated\n');
} catch (err) {
  console.error('Error validating Terms:', err.message);
  allValid = false;
}

// Validate Privacy Policy
try {
  const privacy = JSON.parse(readFileSync('content-templates/legal/privacy.json', 'utf8'));
  console.log('Validating Privacy Policy...');
  const privacyResult = validateContent('privacy-policy', privacy);
  if (!privacyResult.valid) {
    allValid = false;
    errors.push(`Privacy Policy: ${privacyResult.errors.join(', ')}`);
  }
  if (privacyResult.warnings.length > 0) {
    warnings.push(`Privacy Policy: ${privacyResult.warnings.join(', ')}`);
  }
  console.log('✓ Privacy Policy validated\n');
} catch (err) {
  console.error('Error validating Privacy Policy:', err.message);
  allValid = false;
}

// Validate Risk Warning
try {
  const risk = JSON.parse(readFileSync('content-templates/legal/risk_warning.json', 'utf8'));
  console.log('Validating Risk Warning...');
  const riskResult = validateContent('risk-warning', risk);
  if (!riskResult.valid) {
    allValid = false;
    errors.push(`Risk Warning: ${riskResult.errors.join(', ')}`);
  }
  if (riskResult.warnings.length > 0) {
    warnings.push(`Risk Warning: ${riskResult.warnings.join(', ')}`);
  }
  console.log('✓ Risk Warning validated\n');
} catch (err) {
  console.error('Error validating Risk Warning:', err.message);
  allValid = false;
}

// Summary
console.log('='.repeat(50));
console.log('VALIDATION SUMMARY');
console.log('='.repeat(50));

if (warnings.length > 0) {
  console.log('\n⚠️  Warnings:');
  warnings.forEach(w => console.log(`  - ${w}`));
}

if (errors.length > 0) {
  console.log('\n❌ Validation Errors:');
  errors.forEach(e => console.log(`  - ${e}`));
}

if (allValid) {
  console.log('\n✅ All content validated successfully!');
  console.log('\nContent Summary:');
  console.log('  - Articles: 30');
  console.log('  - FAQs: 50');
  console.log('  - Legal documents: 3');
  process.exit(0);
} else {
  console.log('\n❌ Validation failed. Please fix the errors above.');
  process.exit(1);
}

