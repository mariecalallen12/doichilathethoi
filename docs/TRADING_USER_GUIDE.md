# Trading User Guide

**Version:** 1.0.0  
**Last Updated:** 2025-12-16

---

## Getting Started

### 1. Account Setup

Before you can start trading, ensure your account is set up:

1. **Register**: Create an account at `/register`
2. **Verify**: Complete email/phone verification
3. **KYC**: Complete KYC verification (if required)
4. **Deposit**: Add funds to your trading account

### 2. Access Trading Dashboard

Navigate to `/trading` to access the trading dashboard.

---

## Placing Orders

### Order Types

#### Market Order
Executes immediately at current market price.

**When to use**: When you want immediate execution

**Example**:
- Symbol: BTCUSDT
- Side: Buy
- Type: Market
- Quantity: 0.001

#### Limit Order
Executes only when price reaches your specified limit.

**When to use**: When you want to buy/sell at a specific price

**Example**:
- Symbol: BTCUSDT
- Side: Buy
- Type: Limit
- Quantity: 0.001
- Price: 40000.0

#### Stop Order
Triggers when price reaches stop price, then executes as market order.

**When to use**: For stop-loss or take-profit orders

**Example**:
- Symbol: BTCUSDT
- Side: Sell
- Type: Stop
- Quantity: 0.001
- Price: 35000.0
- Stop Price: 34000.0

### Order Placement Steps

1. Select trading pair (e.g., BTCUSDT)
2. Choose order type (Market/Limit/Stop)
3. Select side (Buy/Sell)
4. Enter quantity
5. Enter price (for Limit/Stop orders)
6. Click "Place Order"

### Order Status

- **Pending**: Order is being processed
- **Open**: Order is active and waiting for execution
- **Partial**: Order is partially filled
- **Filled**: Order is completely executed
- **Cancelled**: Order was cancelled
- **Rejected**: Order was rejected (insufficient balance, etc.)

---

## Managing Positions

### Viewing Positions

Navigate to the Positions panel in the trading dashboard to see:
- Open positions
- Entry price
- Current price
- Unrealized P&L
- Position size

### Closing Positions

1. Find the position in the Positions list
2. Click "Close Position"
3. Confirm the action

---

## Risk Management

### Pre-Trade Warnings

The system will warn you if:
- Your order value is very large
- You're approaching daily loss limit
- Your position size is near maximum

### Risk Limits

- **Maximum Position Size**: $1,000,000
- **Daily Loss Limit**: $10,000
- **Minimum Margin**: 10%

---

## Real-Time Updates

### WebSocket Connection

The trading dashboard automatically connects to WebSocket for real-time updates:
- Order status changes
- Position updates
- Account balance changes
- Price updates

### Connection Status

Check the connection indicator in the dashboard:
- 🟢 Green: Connected
- 🟡 Yellow: Reconnecting
- 🔴 Red: Disconnected

---

## Troubleshooting

### Order Not Executing

**Possible causes**:
- Insufficient balance
- Market closed
- Order price too far from market

**Solution**: Check your balance and order details

### Position Not Showing

**Possible causes**:
- Order not yet filled
- Position closed
- Filter applied

**Solution**: Check order status and remove filters

### WebSocket Disconnected

**Solution**: 
- Refresh the page
- Check your internet connection
- Wait for automatic reconnection

---

## Best Practices

1. **Start Small**: Begin with small orders to learn the system
2. **Use Stop Orders**: Always set stop-loss for risk management
3. **Monitor Positions**: Regularly check your open positions
4. **Understand Risks**: Trading involves risk of loss
5. **Keep Learning**: Use Education section to improve skills

---

## Support

For trading support:
- Help Center: `/help`
- Contact: `/contact`
- FAQ: `/faq`

---

**Last Updated:** 2025-12-16

