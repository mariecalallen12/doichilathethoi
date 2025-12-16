# Content Population Guide

## Overview

This guide provides instructions and templates for populating content for Education, Support, and Legal modules.

## Education Module Content

### Videos

Create video entries with the following structure:
- Title: Descriptive title
- Description: Detailed description
- Video URL: Link to video (YouTube, Vimeo, or hosted)
- Thumbnail URL: Preview image
- Category: beginner, intermediate, advanced, strategy, etc.
- Duration: Video length in seconds
- Language: en, vi, etc.

**Sample Video Data:**
```json
{
  "title": "Introduction to Forex Trading",
  "description": "Learn the basics of forex trading",
  "video_url": "https://example.com/videos/intro-forex.mp4",
  "thumbnail_url": "https://example.com/thumbnails/intro-forex.jpg",
  "category": "beginner",
  "duration": 1200,
  "language": "en",
  "tags": ["forex", "beginner", "introduction"],
  "is_featured": true
}
```

### Ebooks

Create ebook entries with:
- Title: Book title
- Description: Book description
- File URL: PDF or ebook file
- Cover URL: Book cover image
- Category: strategy, analysis, psychology, etc.

**Sample Ebook Data:**
```json
{
  "title": "Complete Trading Strategy Guide",
  "description": "Comprehensive guide to trading strategies",
  "file_url": "https://example.com/ebooks/strategy-guide.pdf",
  "cover_url": "https://example.com/covers/strategy-guide.jpg",
  "category": "strategy",
  "language": "en",
  "tags": ["strategy", "guide", "trading"]
}
```

### Economic Calendar Events

Create calendar events with:
- Event name
- Country/Currency
- Impact level: low, medium, high
- Date/Time
- Category: economic indicator, central bank, etc.

**Sample Calendar Event:**
```json
{
  "event_name": "US Non-Farm Payrolls",
  "country": "US",
  "currency": "USD",
  "impact": "high",
  "event_date": "2025-01-10T08:30:00Z",
  "category": "employment",
  "description": "Monthly employment data"
}
```

### Market Reports

Create reports with:
- Title: Report title
- Summary: Executive summary
- Content: Full report content or file URL
- Report date: Publication date
- Period: Start and end dates

**Sample Report:**
```json
{
  "title": "Weekly Market Analysis - Week 1, 2025",
  "summary": "Market overview for the first week of 2025",
  "content": "Full report content...",
  "report_date": "2025-01-07",
  "period_start": "2025-01-01",
  "period_end": "2025-01-07",
  "category": "weekly",
  "is_featured": true
}
```

## Support Module Content

### Help Articles

Create articles with:
- Title: Article title
- Content: Article body (HTML or markdown)
- Category: Account, Trading, Deposits, Withdrawals, etc.
- Tags: Relevant tags
- Is featured: Boolean
- Is pinned: Boolean

**Sample Article:**
```json
{
  "title": "How to Deposit Funds",
  "content": "<h2>Depositing Funds</h2><p>To deposit funds...</p>",
  "category_id": 1,
  "tags": ["deposit", "funding", "account"],
  "is_featured": true,
  "is_pinned": false,
  "language": "en"
}
```

### FAQ Items

Create FAQ entries with:
- Question: FAQ question
- Answer: Detailed answer
- Category: General, Trading, Account, etc.
- Is featured: Boolean

**Sample FAQ:**
```json
{
  "question": "How do I reset my password?",
  "answer": "To reset your password, click on 'Forgot Password'...",
  "category": "account",
  "is_featured": true,
  "language": "en"
}
```

### Office Locations

Create office entries with:
- Name: Office name
- Address: Full address
- City, Country
- Phone, Email
- Opening hours
- Coordinates (lat/lng)

**Sample Office:**
```json
{
  "name": "Headquarters",
  "address": "123 Trading Street",
  "city": "London",
  "country": "UK",
  "phone": "+44 20 1234 5678",
  "email": "support@example.com",
  "opening_hours": "Mon-Fri 9:00-18:00 GMT"
}
```

### Support Channels

Create channel entries with:
- Name: Channel name
- Type: email, phone, chat, etc.
- Value: Contact value
- Availability: Hours or "24/7"
- Response time: Expected response time

**Sample Channel:**
```json
{
  "name": "Email Support",
  "type": "email",
  "value": "support@example.com",
  "availability": "24/7",
  "response_time": "Within 24 hours"
}
```

## Legal Module Content

### Terms of Service

Create terms with:
- Version: Version number (e.g., "1.0")
- Content: Full terms content (HTML or markdown)
- Effective date: When terms take effect
- Language: en, vi, etc.

**Sample Terms:**
```json
{
  "version": "1.0",
  "content": "<h1>Terms of Service</h1><p>These terms...</p>",
  "effective_date": "2025-01-01",
  "language": "en"
}
```

### Privacy Policy

Similar structure to Terms:
```json
{
  "version": "1.0",
  "content": "<h1>Privacy Policy</h1><p>We respect your privacy...</p>",
  "effective_date": "2025-01-01",
  "language": "en"
}
```

### Risk Warning

Create risk warning with:
- Content: Full warning text
- Language: en, vi, etc.
- Version: Version number

**Sample Risk Warning:**
```json
{
  "content": "<h1>Risk Warning</h1><p>Trading involves risk...</p>",
  "language": "en",
  "version": "1.0"
}
```

## Database Seeding

### Using Backend API

You can populate content via:
1. Admin API endpoints (if available)
2. Direct database insertion
3. Seeding scripts

### Seeding Script Template

Create a Python script to seed the database:

```python
# backend/scripts/seed_content.py
from app.db.session import SessionLocal
from app.models.education import Video, Ebook, CalendarEvent, Report
from app.models.support import Article, FAQ, Office, Channel
from app.models.legal import Terms, Privacy, RiskWarning

def seed_education_content(db):
    # Seed videos
    videos = [
        Video(title="...", description="...", ...),
        # Add more videos
    ]
    db.add_all(videos)
    
    # Seed ebooks, calendar, reports similarly
    db.commit()

def seed_support_content(db):
    # Seed articles, FAQ, offices, channels
    pass

def seed_legal_content(db):
    # Seed terms, privacy, risk warning
    pass

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_education_content(db)
        seed_support_content(db)
        seed_legal_content(db)
    finally:
        db.close()
```

## Content Requirements

### Minimum Content for Launch

**Education:**
- 10-15 video tutorials
- 5-10 ebooks
- Weekly economic calendar events
- 4-8 market reports (weekly/monthly)

**Support:**
- 20-30 help articles
- 30-50 FAQ items
- 2-3 office locations
- 3-5 support channels

**Legal:**
- Terms of Service (current version)
- Privacy Policy (current version)
- Risk Warning (current version)

## Content Management

### Best Practices

1. **Version Control**: Keep legal documents versioned
2. **Localization**: Support multiple languages
3. **Categorization**: Use consistent categories
4. **Tags**: Use relevant tags for searchability
5. **Featured Content**: Mark important content as featured
6. **Regular Updates**: Keep content current

### Content Review Process

1. Draft content
2. Review for accuracy
3. Legal review (for legal content)
4. Translation (if needed)
5. Publish
6. Monitor and update

## Next Steps

1. Create content templates
2. Write initial content
3. Set up database seeding
4. Populate test data
5. Review and refine
6. Launch with minimum viable content
7. Continuously add more content

