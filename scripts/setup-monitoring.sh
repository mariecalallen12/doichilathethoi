#!/bin/bash
set -e

echo "📊 Setting up Monitoring Stack"
echo "=============================="
echo ""

# Check if docker-compose.monitoring.yml exists
if [ ! -f "docker-compose.monitoring.yml" ]; then
    echo "❌ docker-compose.monitoring.yml not found!"
    exit 1
fi

# Create required directories
echo "📁 Creating directories..."
mkdir -p prometheus grafana/provisioning/datasources grafana/dashboards alertmanager
echo "✅ Directories created"
echo ""

# Create Prometheus config if it doesn't exist
if [ ! -f "prometheus/prometheus.yml" ]; then
    echo "📝 Creating Prometheus configuration..."
    cat > prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'digital-utopia'
    environment: 'production'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['digital_utopia_backend:8000']
    metrics_path: '/api/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
EOF
    echo "✅ Prometheus config created"
fi

# Create Alertmanager config if it doesn't exist
if [ ! -f "alertmanager/config.yml" ]; then
    echo "📝 Creating Alertmanager configuration..."
    cat > alertmanager/config.yml << 'EOF'
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical'

receivers:
  - name: 'default'
    email_configs:
      - to: 'admin@cmeetrading.com'
        from: 'alerts@cmeetrading.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@cmeetrading.com'
        auth_password: 'your-app-password'

  - name: 'critical'
    email_configs:
      - to: 'admin@cmeetrading.com'
        from: 'alerts@cmeetrading.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@cmeetrading.com'
        auth_password: 'your-app-password'
EOF
    echo "✅ Alertmanager config created"
    echo "⚠️  Please update email configuration in alertmanager/config.yml"
fi

# Create Grafana datasource provisioning
if [ ! -f "grafana/provisioning/datasources/prometheus.yml" ]; then
    echo "📝 Creating Grafana datasource configuration..."
    mkdir -p grafana/provisioning/datasources
    cat > grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF
    echo "✅ Grafana datasource config created"
fi

# Start monitoring stack
echo "🚀 Starting monitoring stack..."
docker-compose -f docker-compose.monitoring.yml up -d

echo ""
echo "✅ Monitoring stack started!"
echo ""
echo "📊 Access URLs:"
echo "   Prometheus:  http://localhost:9090"
echo "   Grafana:     http://localhost:3000 (admin/admin)"
echo "   cAdvisor:    http://localhost:8080"
echo "   Node Exporter: http://localhost:9100/metrics"
echo "   Alertmanager:  http://localhost:9093"
echo ""
echo "⚠️  Remember to:"
echo "   1. Change Grafana admin password"
echo "   2. Update Alertmanager email configuration"
echo "   3. Import dashboards in Grafana"
echo ""
