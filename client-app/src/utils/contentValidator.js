/**
 * Content Validation Utility
 * Validates content before submission to ensure quality and completeness
 */

/**
 * Validate video content
 */
export function validateVideo(video) {
  const errors = [];
  const warnings = [];

  if (!video.title || video.title.trim().length === 0) {
    errors.push('Title is required');
  } else if (video.title.length < 5) {
    warnings.push('Title is very short (minimum 5 characters recommended)');
  }

  if (!video.description || video.description.trim().length === 0) {
    errors.push('Description is required');
  } else if (video.description.length < 20) {
    warnings.push('Description is very short (minimum 20 characters recommended)');
  }

  if (!video.video_url) {
    errors.push('Video URL is required');
  } else if (!isValidUrl(video.video_url)) {
    errors.push('Video URL is invalid');
  }

  if (video.thumbnail_url && !isValidUrl(video.thumbnail_url)) {
    errors.push('Thumbnail URL is invalid');
  }

  if (!video.category) {
    errors.push('Category is required');
  }

  if (!video.duration || video.duration <= 0) {
    errors.push('Duration must be greater than 0');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Validate ebook content
 */
export function validateEbook(ebook) {
  const errors = [];
  const warnings = [];

  if (!ebook.title || ebook.title.trim().length === 0) {
    errors.push('Title is required');
  }

  if (!ebook.description || ebook.description.trim().length === 0) {
    errors.push('Description is required');
  }

  if (!ebook.file_url) {
    errors.push('File URL is required');
  } else if (!isValidUrl(ebook.file_url)) {
    errors.push('File URL is invalid');
  } else if (!ebook.file_url.toLowerCase().endsWith('.pdf')) {
    warnings.push('File should be a PDF');
  }

  if (!ebook.category) {
    errors.push('Category is required');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Validate article content
 */
export function validateArticle(article) {
  const errors = [];
  const warnings = [];

  if (!article.title || article.title.trim().length === 0) {
    errors.push('Title is required');
  }

  if (!article.content || article.content.trim().length === 0) {
    errors.push('Content is required');
  } else if (article.content.length < 100) {
    warnings.push('Content is very short (minimum 100 characters recommended)');
  }

  if (!article.category_id) {
    errors.push('Category is required');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Validate FAQ content
 */
export function validateFAQ(faq) {
  const errors = [];
  const warnings = [];

  if (!faq.question || faq.question.trim().length === 0) {
    errors.push('Question is required');
  } else if (faq.question.length < 10) {
    warnings.push('Question is very short');
  }

  if (!faq.answer || faq.answer.trim().length === 0) {
    errors.push('Answer is required');
  } else if (faq.answer.length < 20) {
    warnings.push('Answer is very short (minimum 20 characters recommended)');
  }

  if (!faq.category) {
    errors.push('Category is required');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Validate legal document
 */
export function validateLegalDocument(doc) {
  const errors = [];
  const warnings = [];

  if (!doc.content || doc.content.trim().length === 0) {
    errors.push('Content is required');
  } else if (doc.content.length < 500) {
    warnings.push('Legal document content is very short');
  }

  if (doc.version && !/^\d+\.\d+$/.test(doc.version)) {
    warnings.push('Version should follow semantic versioning (e.g., 1.0)');
  }

  if (doc.effective_date && !isValidDate(doc.effective_date)) {
    errors.push('Effective date is invalid');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Helper: Check if URL is valid
 */
function isValidUrl(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Helper: Check if date is valid
 */
function isValidDate(dateString) {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date);
}

/**
 * Validate all content types
 */
export function validateContent(type, content) {
  const validators = {
    video: validateVideo,
    ebook: validateEbook,
    article: validateArticle,
    faq: validateFAQ,
    'terms-of-service': validateLegalDocument,
    'privacy-policy': validateLegalDocument,
    'risk-warning': validateLegalDocument,
  };

  const validator = validators[type];
  if (!validator) {
    return {
      valid: false,
      errors: [`Unknown content type: ${type}`],
      warnings: [],
    };
  }

  return validator(content);
}


