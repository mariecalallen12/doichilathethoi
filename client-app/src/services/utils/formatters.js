/**
 * Formatting utilities for trading dashboard
 */

export function formatPrice(price, decimals = 4) {
  if (price === null || price === undefined) return '0.0000';
  
  if (price > 1000) {
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
  
  return price.toFixed(decimals);
}

export function formatPercent(percent, decimals = 2) {
  if (percent === null || percent === undefined) return '0.00';
  return Math.abs(percent).toFixed(decimals);
}

export function formatCurrency(amount, currency = 'USD', locale = 'en-US') {
  // Use Vietnamese locale for VND
  const useLocale = currency === 'VND' ? 'vi-VN' : locale;
  
  return new Intl.NumberFormat(useLocale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined) return '0.00';
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatDate(date, format = 'short', locale = 'vi-VN') {
  if (!date) return '';
  
  const d = new Date(date);
  
  if (format === 'short') {
    return d.toLocaleDateString(locale, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }
  
  if (format === 'long') {
    return d.toLocaleDateString(locale, {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
  
  if (format === 'time') {
    return d.toLocaleTimeString(locale, {
      hour: '2-digit',
      minute: '2-digit',
    });
  }
  
  if (format === 'datetime') {
    return d.toLocaleString(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
  
  return d.toISOString();
}

export function formatTimeAgo(timestamp) {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return 'Just now';
}

export function formatVolume(volume) {
  if (volume >= 1000000) {
    return `${(volume / 1000000).toFixed(2)}M`;
  }
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(2)}K`;
  }
  return volume.toFixed(2);
}

export function getPriceChangeColor(change) {
  if (change > 0) return 'text-green-400';
  if (change < 0) return 'text-red-400';
  return 'text-gray-400';
}

export function getPriceChangeBgColor(change) {
  if (change > 0) return 'bg-green-500/20';
  if (change < 0) return 'bg-red-500/20';
  return 'bg-gray-500/20';
}

