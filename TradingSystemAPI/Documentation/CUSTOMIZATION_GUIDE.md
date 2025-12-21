# 📋 API Data Customization Guide

**Tài liệu hướng dẫn cho nhân viên kỹ thuật**  
**Phiên bản**: 1.0.0  
**Ngày**: 2025-12-21  
**Mục đích**: Hướng dẫn can thiệp và điều chỉnh dữ liệu API theo ý muốn

## 🎯 Tổng Quan

### ✅ Khả Năng Can Thiệp

Hệ thống Trading API cho phép **hoàn toàn can thiệp và tùy chỉnh dữ liệu** trả về để phù hợp với yêu cầu của từng dự án cụ thể. Bạn có thể:

- 🔧 **Điều chỉnh giá cả**: Tăng/giảm giá theo tỷ lệ %
- 📈 **Thay đổi phần trăm**: Tùy chỉnh % thay đổi 24h
- 🎯 **Override tín hiệu**: Buộc signal (BUY/SELL/UP/DOWN)
- 💪 **Boost confidence**: Tăng độ tin cậy
- 📊 **Custom volume**: Đặt volume tùy chỉnh
- 🏢 **Adjust market cap**: Điều chỉnh vốn hóa thị trường

### 🏗️ Vị Trí File

```
TradingSystemAPI/
├── Documentation/Customization/
│   ├── custom_data_manager.py     # Core customization engine
│   └── __init__.py
└── CUSTOMIZATION_GUIDE.md         # Tài liệu này
```

## 🚀 Cách Sử Dụng Cơ Bản

### 1. Import Custom Manager

```python
from Documentation.Customization.custom_data_manager import custom_manager
```

### 2. Tạo Rule Tùy Chỉnh

```python
from Documentation.Customization.custom_data_manager import CustomizationRule

# Tạo rule cho symbol cụ thể
rule = CustomizationRule(
    name="BTC_Bullish_Boost",
    symbol="BTC",
    price_adjustment=5.0,      # +5% price
    change_adjustment=2.0,     # +2% change
    force_signal="STRONG_BUY", # Override signal
    confidence_boost=15.0      # +15% confidence
)

# Thêm rule vào system
custom_manager.add_rule(rule)
```

### 3. Áp Dụng Customizations

```python
# Tự động áp dụng cho tất cả API calls
data = await get_market_data()  # Data sẽ được tự động customize
```

## 📋 Chi Tiết Các Loại Customization

### 🎯 1. Price Adjustment (Điều chỉnh giá)

#### Tăng giá
```python
rule = CustomizationRule(
    name="Price_Increase_10%",
    symbol="BTC",
    price_adjustment=10.0  # Tăng 10%
)
```

#### Giảm giá
```python
rule = CustomizationRule(
    name="Price_Decrease_5%",
    symbol="ETH",
    price_adjustment=-5.0  # Giảm 5%
)
```

#### Áp dụng cho tất cả
```python
rule = CustomizationRule(
    name="Global_Price_Boost",
    symbol="*",  # Áp dụng cho tất cả symbols
    price_adjustment=2.5
)
```

### 📈 2. Change Percentage (Phần trăm thay đổi)

#### Tăng phần trăm
```python
rule = CustomizationRule(
    name="Positive_Change_Boost",
    symbol="XRP",
    change_adjustment=3.0  # Thêm +3% vào change
)
```

#### Giảm phần trăm
```python
rule = CustomizationRule(
    name="Negative_Change",
    symbol="ADA",
    change_adjustment=-2.0  # Trừ 2% từ change
)
```

### 🎯 3. Signal Override (Buộc tín hiệu)

#### Buộc BUY signal
```python
rule = CustomizationRule(
    name="Force_BUY",
    symbol="BTC",
    force_signal="BUY"  # Buộc signal BUY
)
```

#### Buộc SELL signal
```python
rule = CustomizationRule(
    name="Force_SELL",
    symbol="ETH",
    force_signal="SELL"  # Buộc signal SELL
)
```

#### Các signal có thể override
- `"STRONG_BUY"` - Tín hiệu mua mạnh
- `"BUY"` - Tín hiệu mua
- `"UP"` - Xu hướng tăng
- `"DOWN"` - Xu hướng giảm
- `"SELL"` - Tín hiệu bán
- `"STRONG_SELL"` - Tín hiệu bán mạnh

### 💪 4. Confidence Boost (Tăng độ tin cậy)

```python
rule = CustomizationRule(
    name="High_Confidence_BTC",
    symbol="BTC",
    confidence_boost=20.0  # Tăng 20% confidence
)
```

### 📊 5. Volume Customization (Tùy chỉnh volume)

```python
rule = CustomizationRule(
    name="High_Volume_BTC",
    symbol="BTC",
    custom_volume=1000000.0  # Set volume to 1M
)
```

### 🏢 6. Market Cap Adjustment

```python
rule = CustomizationRule(
    name="Market_Cap_Boost",
    symbol="BTC",
    custom_market_cap=2000000000000.0  # $2T market cap
)
```

## 🛠️ Manual Overrides

### Set Manual Price
```python
# Đặt giá cụ thể cho symbol
custom_manager.set_manual_price("BTC", 95000.00)  # $95,000
custom_manager.set_manual_price("XRP", 3.50)     # $3.50
```

### Set Manual Signal
```python
# Buộc signal cụ thể
custom_manager.set_manual_signal("BTC", "STRONG_BUY")
custom_manager.set_manual_signal("ETH", "STRONG_SELL")
```

### Set Confidence Boost
```python
# Tăng confidence
custom_manager.set_confidence_boost("BTC", 25.0)  # +25%
custom_manager.set_confidence_boost("XRP", 30.0)  # +30%
```

## 🎮 Demo Scenarios

### Scenario 1: "Bullish Market Boost"
Tạo thị trường bullish cho campaign marketing

```python
# Setup: Tăng tất cả confidence và force bullish signals
custom_manager.add_rule(CustomizationRule(
    name="Bullish_Campaign",
    symbol="*",  # Tất cả symbols
    price_adjustment=5.0,
    change_adjustment=2.0,
    force_signal="BUY",
    confidence_boost=15.0
))
```

### Scenario 2: "Bearish Market Demo"
Tạo thị trường bearish để test risk management

```python
# Setup: Tạo thị trường bearish
custom_manager.add_rule(CustomizationRule(
    name="Bearish_Test",
    symbol="*",
    price_adjustment=-3.0,
    change_adjustment=-1.5,
    force_signal="SELL",
    confidence_boost=20.0
))
```

### Scenario 3: "VIP Client Treatment"
Đối với khách hàng VIP, tăng chất lượng dữ liệu

```python
# Setup: Tăng chất lượng cho khách VIP
custom_manager.add_rule(CustomizationRule(
    name="VIP_Client",
    symbol="*",
    price_adjustment=1.0,      # Slightly better prices
    change_adjustment=0.5,     # Better changes
    confidence_boost=25.0      # Much higher confidence
))
```

### Scenario 4: "Conservative Signals"
Tín hiệu conservative cho nhà đầu tư thận trọng

```python
# Setup: Giảm độ mạnh tín hiệu
custom_manager.add_rule(CustomizationRule(
    name="Conservative_Signals",
    symbol="*",
    confidence_boost=-10.0,  # Giảm confidence
    price_adjustment=-1.0    # Conservative pricing
))
```

## 🔄 Enable/Disable Customizations

### Enable Customizations
```python
custom_manager.enable_customizations()
# Tất cả API calls sẽ được customize
```

### Disable Customizations
```python
custom_manager.disable_customizations()
# API calls trả về data gốc không customize
```

### Clear All Modifications
```python
custom_manager.clear_all_modifications()
# Xóa tất cả rules và overrides
```

## 📊 Monitoring và Debugging

### Xem Active Rules
```python
active_rules = custom_manager.get_active_rules()
print(f"Active rules: {active_rules}")
```

### Check Modifications Applied
```python
# Trong response data sẽ có field "modifications_applied"
{
    "symbol": "BTC",
    "customized_data": {
        "price": 92577.45,
        "signal": "BUY"
    },
    "modifications_applied": {
        "price_changed": True,
        "signal_changed": False,
        "confidence_changed": True
    }
}
```

## 🚀 Integration với API System

### Sử dụng trong Market Data API

```python
# Trong MarketData/providers.py
from Documentation.Customization.custom_data_manager import custom_manager

def apply_customizations(price_data):
    # Apply customizations
    price_data.price = custom_manager.apply_price_modification(
        price_data.symbol, price_data.price
    )
    
    price_data.change_24h = custom_manager.apply_change_modification(
        price_data.symbol, price_data.change_24h
    )
    
    return price_data
```

### Sử dụng trong Trading Features API

```python
# Trong TradingFeatures/signals.py
from Documentation.Customization.custom_data_manager import custom_manager

def generate_customized_signal(symbol, original_signal):
    # Override signal if configured
    customized_signal = custom_manager.apply_signal_override(
        symbol, original_signal
    )
    
    # Boost confidence
    customized_confidence = custom_manager.apply_confidence_boost(
        symbol, original_confidence
    )
    
    return customized_signal, customized_confidence
```

## 🎯 Use Cases Thực Tế

### 1. Marketing Campaigns
- **Goal**: Tạo dữ liệu tích cực để thu hút khách hàng
- **Customization**: Tăng confidence, force bullish signals
- **Code**:
```python
custom_manager.add_rule(CustomizationRule(
    name="Marketing_Campaign",
    symbol="*",
    confidence_boost=20.0,
    force_signal="BUY",
    price_adjustment=2.0
))
```

### 2. Risk Testing
- **Goal**: Test hệ thống với dữ liệu xấu
- **Customization**: Giảm confidence, force bearish signals
- **Code**:
```python
custom_manager.add_rule(CustomizationRule(
    name="Risk_Test",
    symbol="*",
    confidence_boost=-15.0,
    force_signal="SELL",
    price_adjustment=-5.0
))
```

### 3. A/B Testing
- **Goal**: So sánh hiệu suất với dữ liệu khác nhau
- **Customization**: Tạo 2 versions khác nhau
- **Code**:
```python
# Version A: Conservative
custom_manager.add_rule(CustomizationRule(
    name="Version_A",
    symbol="*",
    confidence_boost=10.0,
    price_adjustment=0.5
))

# Version B: Aggressive  
custom_manager.add_rule(CustomizationRule(
    name="Version_B",
    symbol="*",
    confidence_boost=25.0,
    price_adjustment=3.0
))
```

### 4. Client-Specific Data
- **Goal**: Dữ liệu khác nhau cho từng client
- **Customization**: Symbol-specific rules
- **Code**:
```python
# Client A chỉ quan tâm BTC
custom_manager.add_rule(CustomizationRule(
    name="Client_A_Preferences",
    symbol="BTC",
    confidence_boost=30.0,
    force_signal="STRONG_BUY"
))

# Client B thích ETH
custom_manager.add_rule(CustomizationRule(
    name="Client_B_Preferences", 
    symbol="ETH",
    confidence_boost=25.0,
    force_signal="BUY"
))
```

### 5. Demo Presentations
- **Goal**: Dữ liệu ấn tượng cho presentations
- **Customization**: Tăng tối đa performance metrics
- **Code**:
```python
custom_manager.add_rule(CustomizationRule(
    name="Demo_Presentation",
    symbol="*",
    price_adjustment=10.0,
    change_adjustment=5.0,
    confidence_boost=35.0,
    force_signal="STRONG_BUY"
))
```

## ⚠️ Best Practices

### 1. Ghi Log Rõ Ràng
```python
# Luôn log khi apply customizations
print(f"Applied customization for {symbol}: {modification_type}")
```

### 2. Validate Customizations
```python
def validate_customization(rule):
    if rule.price_adjustment > 50:  # Không cho phép tăng quá 50%
        raise ValueError("Price adjustment too large")
```

### 3. Backup Original Data
```python
def apply_customization_safely(symbol, original_data):
    backup = original_data.copy()  # Backup data gốc
    customized = apply_customizations(original_data)
    return customized, backup
```

### 4. Reset After Use
```python
# Reset customizations sau khi sử dụng
custom_manager.disable_customizations()
custom_manager.clear_all_modifications()
```

### 5. Document Customizations
```python
# Comment rõ ràng mục đích
# This rule makes BTC more attractive for VIP client demo
custom_manager.add_rule(CustomizationRule(
    name="VIP_Demo_BTC_Boost",
    symbol="BTC",
    confidence_boost=25.0,
    force_signal="STRONG_BUY"
))
```

## 🔧 Advanced Features

### 1. Conditional Customizations
```python
# Áp dụng rule dựa trên điều kiện
def conditional_rule_based_on_time():
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 17:  # Business hours
        custom_manager.add_rule(CustomizationRule(
            name="Business_Hours_Boost",
            symbol="*",
            confidence_boost=10.0
        ))
```

### 2. Percentage-based Adjustments
```python
# Điều chỉnh dựa trên % của giá gốc
def apply_percentage_based_adjustment(symbol, price, adjustment_percent):
    adjustment_amount = price * (adjustment_percent / 100)
    return price + adjustment_amount
```

### 3. Time-based Customizations
```python
# Customizations thay đổi theo thời gian
def time_based_customization():
    if datetime.now().weekday() == 0:  # Monday
        custom_manager.add_rule(CustomizationRule(
            name="Monday_Bullish",
            symbol="*",
            force_signal="BUY"
        ))
```

## 🧪 Testing Customizations

### Unit Test
```python
def test_price_adjustment():
    custom_manager.add_rule(CustomizationRule(
        name="Test_5_Percent_Increase",
        symbol="BTC",
        price_adjustment=5.0
    ))
    
    original_price = 50000.0
    adjusted_price = custom_manager.apply_price_modification("BTC", original_price)
    
    assert adjusted_price == 52500.0  # 5% increase
    print("✅ Price adjustment test passed")
```

### Integration Test
```python
async def test_full_customization():
    # Setup customizations
    custom_manager.add_rule(CustomizationRule(
        name="Integration_Test",
        symbol="BTC",
        price_adjustment=10.0,
        force_signal="BUY"
    ))
    
    # Get data
    data = await get_market_data()
    
    # Verify customizations applied
    assert data["BTC"]["signal"] == "BUY"
    assert data["BTC"]["price"] > original_btc_price
    
    print("✅ Integration test passed")
```

## 📞 Troubleshooting

### Common Issues

#### 1. Customizations Not Applied
```python
# Check if customizations are enabled
print(f"Active customizations: {custom_manager.active_customizations}")

# Enable if disabled
custom_manager.enable_customizations()
```

#### 2. Rules Not Working
```python
# Check active rules
active_rules = custom_manager.get_active_rules()
print(f"Active rules: {active_rules}")

# Re-add rule if missing
custom_manager.add_rule(your_rule)
```

#### 3. Unexpected Results
```python
# Clear all and start fresh
custom_manager.clear_all_modifications()
custom_manager.enable_customizations()
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Customizations sẽ log chi tiết
```

## 🎉 Kết Luận

Hệ thống Custom Data Manager cung cấp **hoàn toàn khả năng can thiệp** vào dữ liệu API để phù hợp với bất kỳ yêu cầu nào của dự án. Với các tính năng:

- ✅ **Flexible Customization**: Điều chỉnh mọi aspect của data
- ✅ **Real-time Application**: Áp dụng ngay lập tức
- ✅ **Safe and Reversible**: Có thể enable/disable any time
- ✅ **Multiple Scenarios**: Hỗ trợ nhiều use cases
- ✅ **Developer Friendly**: API đơn giản và rõ ràng

**Nhân viên kỹ thuật có thể hoàn toàn kiểm soát dữ liệu trả về cho ứng dụng tích hợp!**

---

**📧 Support**: Nếu cần hỗ trợ thêm, vui lòng liên hệ team development  
**📖 Related**: Xem thêm README.md cho overview hệ thống  
**🔧 Examples**: Tham khảo demo.py để xem examples đầy đủ