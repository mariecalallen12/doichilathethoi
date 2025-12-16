# Load Testing với k6

## Cài đặt k6

### Linux
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### macOS
```bash
brew install k6
```

### Docker
```bash
docker run --rm -i grafana/k6 run - <tests/load/websocket_test.js
```

## Chạy Load Test

### Test cơ bản (1000 connections)
```bash
k6 run tests/load/websocket_test.js
```

### Test với custom URL
```bash
WS_URL=wss://cmeetrading.com/ws API_BASE=https://cmeetrading.com/api k6 run tests/load/websocket_test.js
```

### Test với output file
```bash
k6 run --out json=results.json tests/load/websocket_test.js
```

### Test với custom stages
Chỉnh sửa `options.stages` trong file test để customize load pattern.

## Metrics

k6 sẽ track các metrics sau:
- `errors`: Tỷ lệ lỗi
- `ws_connecting`: Tỷ lệ kết nối thành công
- `ws_session_duration`: Thời gian session
- `messages_received`: Tỷ lệ nhận messages
- `ws_messages_sent`: Số messages đã gửi
- `ws_messages_received`: Số messages đã nhận

## Thresholds

Test sẽ fail nếu:
- Error rate > 1%
- Connection failure rate > 10%
- 95% sessions > 5s
- Message rate < 80%

## Kết quả mong đợi

Với 10k connections:
- Latency < 30ms (internal network)
- Error rate < 1%
- Message rate > 80%
- CPU usage < 80%
- Memory usage < 4GB

## Troubleshooting

### Connection refused
- Kiểm tra WebSocket server đang chạy
- Kiểm tra firewall/port
- Kiểm tra URL đúng

### High error rate
- Kiểm tra server logs
- Giảm số connections
- Tăng timeout

### High latency
- Kiểm tra network
- Tối ưu database queries
- Tăng server resources

