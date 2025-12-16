# Technical Review: Order Book Simulator & Matching Engine

## Tổng quan

Tài liệu này đánh giá các phương pháp và công nghệ để triển khai Order Book Simulator và Matching Engine cho hệ thống Market-Maker Engine.

## 1. Cấu trúc Order Book

### 1.1. Tree-based (Red-Black Tree / AVL Tree)

**Ưu điểm:**
- O(log n) cho insert/delete/search
- Tự động sắp xếp theo giá
- Phù hợp cho high-frequency trading
- Được sử dụng bởi các exchange lớn (Binance, Coinbase)

**Nhược điểm:**
- Phức tạp hơn trong implementation
- Overhead memory cao hơn
- Cần cân bằng tree

**Ví dụ implementation:**
```python
# Sử dụng sortedcontainers hoặc tự implement Red-Black Tree
from sortedcontainers import SortedDict

class OrderBook:
    def __init__(self):
        self.bids = SortedDict()  # price -> quantity
        self.asks = SortedDict()
```

### 1.2. HashMap + Sorted List

**Ưu điểm:**
- Đơn giản hơn trong implementation
- O(1) lookup theo price
- Dễ debug và maintain

**Nhược điểm:**
- O(n log n) khi sort lại
- Không tối ưu cho high-frequency

**Ví dụ implementation:**
```python
class OrderBook:
    def __init__(self):
        self.bids = {}  # price -> quantity
        self.asks = {}
        self._sorted_bids = []
        self._sorted_asks = []
```

### 1.3. Quyết định cho dự án

**Chọn: HashMap + Sorted List**
- Phù hợp với yêu cầu latency <30ms (không phải microsecond)
- Dễ maintain và debug
- Đủ hiệu năng cho simulator (không phải production exchange)
- Có thể nâng cấp lên Tree sau nếu cần

## 2. Thuật toán Matching

### 2.1. Price-Time Priority

**Nguyên tắc:**
1. Ưu tiên giá tốt nhất (best price)
2. Trong cùng giá, ưu tiên lệnh đến trước (FIFO)

**Implementation:**
```python
class MatchingEngine:
    def match_order(self, order: Order, orderbook: OrderBook):
        if order.side == "buy":
            # Tìm best ask (giá thấp nhất)
            best_ask = orderbook.get_best_ask()
            if best_ask and order.price >= best_ask.price:
                # Khớp lệnh
                return self._execute_match(order, best_ask)
        else:
            # Tìm best bid (giá cao nhất)
            best_bid = orderbook.get_best_bid()
            if best_bid and order.price <= best_bid.price:
                return self._execute_match(order, best_bid)
```

### 2.2. Partial Fills

**Xử lý:**
- Lệnh có thể khớp một phần
- Tạo nhiều trades từ một order
- Cập nhật orderbook sau mỗi trade

### 2.3. Quyết định

**Implement đầy đủ Price-Time Priority với Partial Fills**

## 3. Công nghệ Stack

### 3.1. Node.js/TypeScript

**Ưu điểm:**
- Event-driven, phù hợp real-time
- Ecosystem phong phú
- Dễ tích hợp WebSocket

**Nhược điểm:**
- Single-threaded (cần cluster cho scale)
- Không phù hợp với codebase hiện tại (Python)

### 3.2. Golang

**Ưu điểm:**
- Performance cao
- Concurrent tốt (goroutines)
- Phù hợp high-frequency trading

**Nhược điểm:**
- Không phù hợp với codebase hiện tại
- Learning curve cao hơn

### 3.3. Python (FastAPI)

**Ưu điểm:**
- Đã có sẵn trong codebase
- Dễ maintain và integrate
- Đủ hiệu năng cho yêu cầu (<30ms latency)

**Nhược điểm:**
- GIL limitation (nhưng không ảnh hưởng với async)

### 3.4. Quyết định

**Giữ Python (FastAPI)**
- Codebase hiện tại đã dùng Python
- Yêu cầu latency <30ms có thể đạt được
- Dễ maintain và phát triển

## 4. Thuật toán sinh dữ liệu

### 4.1. Random Walk

**Mô hình:**
```
price(t+1) = price(t) + drift * dt + volatility * sqrt(dt) * random()
```

**Ưu điểm:**
- Đơn giản
- Phù hợp mô phỏng cơ bản

**Nhược điểm:**
- Không mô phỏng được jumps
- Không realistic cho crypto

### 4.2. Brownian Motion + Jump-Diffusion

**Mô hình:**
```
dS = μ*S*dt + σ*S*dW + J*dN
```

Trong đó:
- μ: drift
- σ: volatility
- dW: Wiener process (Brownian motion)
- J: jump size
- dN: Poisson process (jump events)

**Ưu điểm:**
- Realistic hơn
- Mô phỏng được volatility clustering
- Phù hợp crypto market

**Nhược điểm:**
- Phức tạp hơn
- Cần tune parameters

### 4.3. Quyết định

**Implement Brownian Motion + Jump-Diffusion**
- Phù hợp với yêu cầu realistic simulation
- Có thể điều chỉnh qua scenario parameters

## 5. Tài liệu tham khảo

### 5.1. Open Source Projects

1. **ccxt** - Crypto exchange library (có orderbook simulation)
2. **orderbook** (Python) - Simple orderbook implementation
3. **matching-engine** (various languages) - Matching engine examples

### 5.2. Papers & Articles

1. "High-Frequency Trading in a Limit Order Market" - Biais et al.
2. "Market Microstructure Theory" - O'Hara
3. "Algorithmic Trading" - Chan

## 6. Kết luận

### 6.1. Cấu trúc Order Book
- **Chọn:** HashMap + Sorted List
- **Lý do:** Đơn giản, đủ hiệu năng, dễ maintain

### 6.2. Matching Algorithm
- **Chọn:** Price-Time Priority với Partial Fills
- **Lý do:** Standard trong industry, đảm bảo fairness

### 6.3. Technology Stack
- **Chọn:** Python (FastAPI) - giữ nguyên
- **Lý do:** Phù hợp codebase, đủ hiệu năng

### 6.4. Data Generation
- **Chọn:** Brownian Motion + Jump-Diffusion
- **Lý do:** Realistic, có thể điều chỉnh qua scenarios

## 7. Next Steps

1. Implement Order Book với HashMap + Sorted List
2. Implement Matching Engine với Price-Time Priority
3. Nâng cấp data generation với Jump-Diffusion
4. Tối ưu latency (<20ms target)
5. Test với load testing (10k connections)

---

**Ngày tạo:** 2025-01-09  
**Phiên bản:** 1.0  
**Tác giả:** Development Team

