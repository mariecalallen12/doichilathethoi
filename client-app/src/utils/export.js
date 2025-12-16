/**
 * Export utilities for CSV and PDF generation
 */

/**
 * Convert array of objects to CSV string
 * @param {Array} data - Array of objects to export
 * @param {Array} columns - Column definitions [{key, label}]
 * @returns {string} CSV string
 */
export function arrayToCSV(data, columns) {
  if (!data || data.length === 0) {
    return '';
  }

  // CSV header
  const header = columns.map(col => `"${col.label}"`).join(',');
  
  // CSV rows
  const rows = data.map(item => {
    return columns.map(col => {
      let value = item[col.key];
      
      // Handle nested objects
      if (col.transform && typeof col.transform === 'function') {
        value = col.transform(value, item);
      } else if (value === null || value === undefined) {
        value = '';
      } else if (typeof value === 'object') {
        value = JSON.stringify(value);
      }
      
      // Escape quotes and wrap in quotes
      value = String(value).replace(/"/g, '""');
      return `"${value}"`;
    }).join(',');
  });

  return [header, ...rows].join('\n');
}

/**
 * Download CSV file
 * @param {string} csvContent - CSV string content
 * @param {string} filename - Filename without extension
 */
export function downloadCSV(csvContent, filename = 'export') {
  const blob = new Blob(['\ufeff', csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Export transactions to CSV
 * @param {Array} transactions - Array of transaction objects
 * @param {Object} options - Export options
 */
export function exportTransactionsToCSV(transactions, options = {}) {
  const {
    filename = 'transactions',
    columns = null,
  } = options;

  // Default columns for transactions
  const defaultColumns = [
    { key: 'date', label: 'Ngày/Giờ' },
    { key: 'type', label: 'Loại' },
    { key: 'currency', label: 'Tiền tệ' },
    { key: 'amount', label: 'Số tiền' },
    { key: 'fee', label: 'Phí' },
    { key: 'status', label: 'Trạng thái' },
    { key: 'reference', label: 'Mã tham chiếu' },
    { key: 'description', label: 'Mô tả' },
  ];

  const exportColumns = columns || defaultColumns;

  // Transform data
  const transformedColumns = exportColumns.map(col => ({
    ...col,
    transform: col.transform || ((value, item) => {
      if (col.key === 'date') {
        return new Date(value).toLocaleString('vi-VN');
      }
      if (col.key === 'amount' || col.key === 'fee') {
        return typeof value === 'number' ? value.toFixed(2) : value;
      }
      if (col.key === 'type') {
        const typeMap = {
          deposit: 'Nạp tiền',
          withdrawal: 'Rút tiền',
          trading: 'Giao dịch',
          order: 'Đặt lệnh',
          fee: 'Phí',
        };
        return typeMap[value] || value;
      }
      if (col.key === 'status') {
        const statusMap = {
          completed: 'Hoàn thành',
          pending: 'Đang xử lý',
          failed: 'Thất bại',
          cancelled: 'Đã hủy',
        };
        return statusMap[value] || value;
      }
      return value;
    }),
  }));

  const csvContent = arrayToCSV(transactions, transformedColumns);
  downloadCSV(csvContent, filename);
}

/**
 * Generate PDF content (using jsPDF library)
 * Note: This requires jsPDF to be installed
 * @param {Array} transactions - Array of transaction objects
 * @param {Object} options - Export options
 */
export async function exportTransactionsToPDF(transactions, options = {}) {
  try {
    // Dynamic import of jsPDF
    const { jsPDF } = await import('jspdf');
    const { autoTable } = await import('jspdf-autotable');

    const {
      filename = 'transactions',
      title = 'Lịch Sử Giao Dịch',
    } = options;

    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(18);
    doc.text(title, 14, 20);
    
    // Add date
    doc.setFontSize(10);
    doc.text(`Ngày xuất: ${new Date().toLocaleString('vi-VN')}`, 14, 30);

    // Prepare table data
    const tableData = transactions.map(t => [
      new Date(t.date).toLocaleString('vi-VN'),
      getTypeLabel(t.type),
      t.currency || 'N/A',
      formatCurrency(t.amount, t.currency),
      formatCurrency(t.fee || 0, t.currency),
      getStatusLabel(t.status),
      t.reference || 'N/A',
      t.description || '',
    ]);

    // Add table
    autoTable(doc, {
      head: [['Ngày/Giờ', 'Loại', 'Tiền tệ', 'Số tiền', 'Phí', 'Trạng thái', 'Mã tham chiếu', 'Mô tả']],
      body: tableData,
      startY: 35,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [139, 92, 246] }, // Purple color
    });

    // Save PDF
    doc.save(`${filename}_${new Date().toISOString().split('T')[0]}.pdf`);
  } catch (error) {
    console.error('Error generating PDF:', error);
    throw new Error('PDF export requires jsPDF library. Please install: npm install jspdf jspdf-autotable');
  }
}

/**
 * Helper functions
 */
function getTypeLabel(type) {
  const typeMap = {
    deposit: 'Nạp tiền',
    withdrawal: 'Rút tiền',
    trading: 'Giao dịch',
    order: 'Đặt lệnh',
    fee: 'Phí',
  };
  return typeMap[type] || type;
}

function getStatusLabel(status) {
  const statusMap = {
    completed: 'Hoàn thành',
    pending: 'Đang xử lý',
    failed: 'Thất bại',
    cancelled: 'Đã hủy',
  };
  return statusMap[status] || status;
}

function formatCurrency(amount, currency = 'USD') {
  if (typeof amount !== 'number') {
    return amount;
  }
  
  const currencySymbols = {
    USD: '$',
    VND: '₫',
    EUR: '€',
    GBP: '£',
    CNY: '¥',
  };
  
  const symbol = currencySymbols[currency] || currency;
  return `${symbol}${amount.toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Export portfolio data to CSV
 * @param {Array} portfolio - Portfolio data
 * @param {string} filename - Filename
 */
export function exportPortfolioToCSV(portfolio, filename = 'portfolio') {
  const columns = [
    { key: 'symbol', label: 'Tài sản' },
    { key: 'quantity', label: 'Số lượng' },
    { key: 'averageCost', label: 'Giá trung bình' },
    { key: 'currentPrice', label: 'Giá hiện tại' },
    { key: 'marketValue', label: 'Giá trị thị trường' },
    { key: 'unrealizedPnl', label: 'Lãi/Lỗ chưa thực hiện' },
  ];

  const csvContent = arrayToCSV(portfolio, columns);
  downloadCSV(csvContent, filename);
}

/**
 * Export any data to Excel-compatible CSV
 * @param {Array} data - Data to export
 * @param {Array} columns - Column definitions
 * @param {string} filename - Filename
 */
export function exportToExcel(data, columns, filename = 'export') {
  const csvContent = arrayToCSV(data, columns);
  downloadCSV(csvContent, filename);
}

