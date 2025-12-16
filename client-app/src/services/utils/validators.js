/**
 * Validation utilities for trading forms
 */

export function validateQuantity(quantity, min = 0.01, max = 1000000) {
  if (!quantity || quantity <= 0) {
    return { valid: false, message: 'Khối lượng phải lớn hơn 0' };
  }
  
  if (quantity < min) {
    return { valid: false, message: `Khối lượng tối thiểu là ${min}` };
  }
  
  if (quantity > max) {
    return { valid: false, message: `Khối lượng tối đa là ${max}` };
  }
  
  return { valid: true };
}

export function validatePrice(price, min = 0.0001, max = 1000000) {
  if (!price || price <= 0) {
    return { valid: false, message: 'Giá phải lớn hơn 0' };
  }
  
  if (price < min) {
    return { valid: false, message: `Giá tối thiểu là ${min}` };
  }
  
  if (price > max) {
    return { valid: false, message: `Giá tối đa là ${max}` };
  }
  
  return { valid: true };
}

export function validateStopLoss(stopLoss, entryPrice, side) {
  if (!stopLoss || stopLoss <= 0) {
    return { valid: true }; // Stop loss is optional
  }
  
  if (side === 'buy' && stopLoss >= entryPrice) {
    return { valid: false, message: 'Stop Loss phải thấp hơn giá vào lệnh' };
  }
  
  if (side === 'sell' && stopLoss <= entryPrice) {
    return { valid: false, message: 'Stop Loss phải cao hơn giá vào lệnh' };
  }
  
  return { valid: true };
}

export function validateTakeProfit(takeProfit, entryPrice, side) {
  if (!takeProfit || takeProfit <= 0) {
    return { valid: true }; // Take profit is optional
  }
  
  if (side === 'buy' && takeProfit <= entryPrice) {
    return { valid: false, message: 'Take Profit phải cao hơn giá vào lệnh' };
  }
  
  if (side === 'sell' && takeProfit >= entryPrice) {
    return { valid: false, message: 'Take Profit phải thấp hơn giá vào lệnh' };
  }
  
  return { valid: true };
}

export function validateOrder(orderData) {
  const errors = [];
  
  // Validate quantity
  const quantityValidation = validateQuantity(orderData.quantity);
  if (!quantityValidation.valid) {
    errors.push(quantityValidation.message);
  }
  
  // Validate price (if limit order)
  if (orderData.type === 'limit' && orderData.price) {
    const priceValidation = validatePrice(orderData.price);
    if (!priceValidation.valid) {
      errors.push(priceValidation.message);
    }
  }
  
  // Validate stop loss
  if (orderData.stopLoss && orderData.price) {
    const stopLossValidation = validateStopLoss(
      orderData.stopLoss,
      orderData.price,
      orderData.side
    );
    if (!stopLossValidation.valid) {
      errors.push(stopLossValidation.message);
    }
  }
  
  // Validate take profit
  if (orderData.takeProfit && orderData.price) {
    const takeProfitValidation = validateTakeProfit(
      orderData.takeProfit,
      orderData.price,
      orderData.side
    );
    if (!takeProfitValidation.valid) {
      errors.push(takeProfitValidation.message);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

export function validateDeposit(amount, min = 10, max = 100000) {
  if (!amount || amount <= 0) {
    return { valid: false, message: 'Số tiền phải lớn hơn 0' };
  }
  
  if (amount < min) {
    return { valid: false, message: `Số tiền tối thiểu là $${min}` };
  }
  
  if (amount > max) {
    return { valid: false, message: `Số tiền tối đa là $${max}` };
  }
  
  return { valid: true };
}

export function validateWithdraw(amount, balance, min = 10) {
  if (!amount || amount <= 0) {
    return { valid: false, message: 'Số tiền phải lớn hơn 0' };
  }
  
  if (amount < min) {
    return { valid: false, message: `Số tiền tối thiểu là $${min}` };
  }
  
  if (amount > balance) {
    return { valid: false, message: 'Số tiền vượt quá số dư khả dụng' };
  }
  
  return { valid: true };
}

