/**
 * Market Data Formatters
 * Utility functions for formatting market data
 */

/**
 * Format price with appropriate decimals
 */
export function formatPrice(price, decimals = 2) {
  if (price === null || price === undefined) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(price);
}

/**
 * Format percentage change
 */
export function formatPercentChange(change, decimals = 2) {
  if (change === null || change === undefined) return '0.00%';
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(decimals)}%`;
}

/**
 * Format volume with K/M/B suffixes
 */
export function formatVolume(volume) {
  if (volume === null || volume === undefined) return 'N/A';
  if (volume >= 1000000000) {
    return `${(volume / 1000000000).toFixed(2)}B`;
  }
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(2)}M`;
  }
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(2)}K`;
  }
  return volume.toFixed(2);
}

/**
 * Format large numbers with commas
 */
export function formatLargeNumber(num) {
  if (num === null || num === undefined) return 'N/A';
  return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Format date for display
 */
export function formatMarketDate(date) {
  if (!date) return 'N/A';
  const d = new Date(date);
  return new Intl.DateTimeFormat('vi-VN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date) {
  if (!date) return 'N/A';
  const now = new Date();
  const diff = now - new Date(date);
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days} ngày trước`;
  if (hours > 0) return `${hours} giờ trước`;
  if (minutes > 0) return `${minutes} phút trước`;
  return 'Vừa xong';
}

/**
 * Get color class based on price change
 */
export function getPriceChangeColor(change) {
  if (change > 0) return 'text-green-400';
  if (change < 0) return 'text-red-400';
  return 'text-gray-400';
}

/**
 * Get background color class based on price change
 */
export function getPriceChangeBgColor(change) {
  if (change > 0) return 'bg-green-500/20';
  if (change < 0) return 'bg-red-500/20';
  return 'bg-gray-500/20';
}

