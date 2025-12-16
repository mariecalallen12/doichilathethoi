#!/usr/bin/env node
/**
 * Script to generate content templates for Education, Support, and Legal modules
 * Helps content team populate content efficiently
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const templates = {
  education: {
    videos: {
      title: "Video Tutorial Template",
      fields: [
        { name: "title", type: "string", required: true, example: "Introduction to Forex Trading" },
        { name: "description", type: "text", required: true, example: "Learn the basics of forex trading" },
        { name: "video_url", type: "url", required: true, example: "https://example.com/videos/intro-forex.mp4" },
        { name: "thumbnail_url", type: "url", required: false, example: "https://example.com/thumbnails/intro-forex.jpg" },
        { name: "category", type: "enum", required: true, options: ["beginner", "intermediate", "advanced", "strategy", "forex", "crypto", "analysis"], example: "beginner" },
        { name: "duration", type: "number", required: true, example: 1200, description: "Duration in seconds" },
        { name: "language", type: "string", required: false, example: "en", default: "en" },
        { name: "tags", type: "array", required: false, example: ["forex", "beginner", "introduction"] },
        { name: "is_featured", type: "boolean", required: false, example: true, default: false }
      ]
    },
    ebooks: {
      title: "Ebook Template",
      fields: [
        { name: "title", type: "string", required: true, example: "Complete Trading Strategy Guide" },
        { name: "description", type: "text", required: true, example: "Comprehensive guide to trading strategies" },
        { name: "file_url", type: "url", required: true, example: "https://example.com/ebooks/strategy-guide.pdf" },
        { name: "cover_url", type: "url", required: false, example: "https://example.com/covers/strategy-guide.jpg" },
        { name: "category", type: "enum", required: true, options: ["strategy", "analysis", "psychology", "risk-management"], example: "strategy" },
        { name: "language", type: "string", required: false, example: "en", default: "en" },
        { name: "tags", type: "array", required: false, example: ["strategy", "guide", "trading"] }
      ]
    },
    calendar: {
      title: "Economic Calendar Event Template",
      fields: [
        { name: "event_name", type: "string", required: true, example: "US Non-Farm Payrolls" },
        { name: "country", type: "string", required: true, example: "US", description: "ISO country code" },
        { name: "currency", type: "string", required: true, example: "USD", description: "ISO currency code" },
        { name: "impact", type: "enum", required: true, options: ["low", "medium", "high"], example: "high" },
        { name: "event_date", type: "datetime", required: true, example: "2025-01-10T08:30:00Z" },
        { name: "category", type: "enum", required: true, options: ["employment", "inflation", "gdp", "central-bank", "trade"], example: "employment" },
        { name: "description", type: "text", required: false, example: "Monthly employment data" },
        { name: "previous_value", type: "string", required: false, example: "150K" },
        { name: "forecast_value", type: "string", required: false, example: "180K" }
      ]
    },
    reports: {
      title: "Market Report Template",
      fields: [
        { name: "title", type: "string", required: true, example: "Weekly Market Analysis - Week 1, 2025" },
        { name: "summary", type: "text", required: true, example: "Market overview for the first week of 2025" },
        { name: "content", type: "text", required: true, example: "Full report content..." },
        { name: "report_date", type: "date", required: true, example: "2025-01-07" },
        { name: "period_start", type: "date", required: false, example: "2025-01-01" },
        { name: "period_end", type: "date", required: false, example: "2025-01-07" },
        { name: "category", type: "enum", required: true, options: ["daily", "weekly", "monthly", "forex", "crypto", "commodities"], example: "weekly" },
        { name: "is_featured", type: "boolean", required: false, example: true, default: false },
        { name: "thumbnail_url", type: "url", required: false, example: "https://example.com/reports/weekly-1.jpg" }
      ]
    }
  },
  support: {
    articles: {
      title: "Help Article Template",
      fields: [
        { name: "title", type: "string", required: true, example: "How to Deposit Funds" },
        { name: "content", type: "html", required: true, example: "<h2>Depositing Funds</h2><p>To deposit funds...</p>" },
        { name: "category_id", type: "number", required: true, example: 1, description: "Category ID from support categories" },
        { name: "tags", type: "array", required: false, example: ["deposit", "funding", "account"] },
        { name: "is_featured", type: "boolean", required: false, example: true, default: false },
        { name: "is_pinned", type: "boolean", required: false, example: false, default: false },
        { name: "language", type: "string", required: false, example: "en", default: "en" }
      ]
    },
    faq: {
      title: "FAQ Item Template",
      fields: [
        { name: "question", type: "string", required: true, example: "How do I reset my password?" },
        { name: "answer", type: "text", required: true, example: "To reset your password, click on 'Forgot Password'..." },
        { name: "category", type: "enum", required: true, options: ["general", "trading", "account", "technical", "legal"], example: "account" },
        { name: "is_featured", type: "boolean", required: false, example: true, default: false },
        { name: "language", type: "string", required: false, example: "en", default: "en" }
      ]
    }
  },
  legal: {
    terms: {
      title: "Terms of Service Template",
      fields: [
        { name: "version", type: "string", required: true, example: "1.0" },
        { name: "content", type: "html", required: true, example: "<h1>Terms of Service</h1><p>...</p>" },
        { name: "effective_date", type: "date", required: true, example: "2025-01-01" },
        { name: "language", type: "string", required: false, example: "en", default: "en" }
      ]
    },
    privacy: {
      title: "Privacy Policy Template",
      fields: [
        { name: "version", type: "string", required: true, example: "1.0" },
        { name: "content", type: "html", required: true, example: "<h1>Privacy Policy</h1><p>...</p>" },
        { name: "effective_date", type: "date", required: true, example: "2025-01-01" },
        { name: "language", type: "string", required: false, example: "en", default: "en" }
      ]
    },
    risk_warning: {
      title: "Risk Warning Template",
      fields: [
        { name: "content", type: "html", required: true, example: "<h1>Risk Warning</h1><p>...</p>" },
        { name: "language", type: "string", required: false, example: "en", default: "en" }
      ]
    }
  }
};

function generateJSONTemplate(category, type, template) {
  const example = {};
  template.fields.forEach(field => {
    if (field.example !== undefined) {
      example[field.name] = field.example;
    } else if (field.default !== undefined) {
      example[field.name] = field.default;
    }
  });
  return JSON.stringify(example, null, 2);
}

function generateMarkdownDocumentation() {
  let md = `# Content Templates Documentation\n\n`;
  md += `Generated: ${new Date().toISOString()}\n\n`;
  md += `This document provides templates and field descriptions for populating content.\n\n`;

  Object.entries(templates).forEach(([category, types]) => {
    md += `## ${category.charAt(0).toUpperCase() + category.slice(1)} Module\n\n`;
    
    Object.entries(types).forEach(([type, template]) => {
      md += `### ${template.title}\n\n`;
      md += `**Type**: \`${type}\`\n\n`;
      md += `**Fields**:\n\n`;
      
      template.fields.forEach(field => {
        md += `- **${field.name}** (${field.type}${field.required ? ', required' : ', optional'})`;
        if (field.description) {
          md += ` - ${field.description}`;
        }
        if (field.options) {
          md += ` - Options: ${field.options.join(', ')}`;
        }
        md += `\n`;
      });
      
      md += `\n**Example JSON**:\n\`\`\`json\n${generateJSONTemplate(category, type, template)}\n\`\`\`\n\n`;
    });
  });

  return md;
}

function main() {
  console.log('📝 Generating content templates...\n');

  // Generate markdown documentation
  const mdContent = generateMarkdownDocumentation();
  const mdPath = path.join(rootDir, 'CONTENT_TEMPLATES.md');
  fs.writeFileSync(mdPath, mdContent);
  console.log(`✅ Generated: ${mdPath}`);

  // Generate JSON templates directory
  const templatesDir = path.join(rootDir, 'content-templates');
  if (!fs.existsSync(templatesDir)) {
    fs.mkdirSync(templatesDir, { recursive: true });
  }

  Object.entries(templates).forEach(([category, types]) => {
    const categoryDir = path.join(templatesDir, category);
    if (!fs.existsSync(categoryDir)) {
      fs.mkdirSync(categoryDir, { recursive: true });
    }

    Object.entries(types).forEach(([type, template]) => {
      const jsonContent = generateJSONTemplate(category, type, template);
      const jsonPath = path.join(categoryDir, `${type}.json`);
      fs.writeFileSync(jsonPath, jsonContent);
      console.log(`✅ Generated: ${jsonPath}`);
    });
  });

  console.log('\n✨ Content templates generated successfully!');
  console.log('\nNext steps:');
  console.log('1. Review CONTENT_TEMPLATES.md for field descriptions');
  console.log('2. Use JSON templates in content-templates/ as starting points');
  console.log('3. Populate content via admin panel or API');
}

main();


