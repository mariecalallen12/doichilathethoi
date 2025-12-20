#!/bin/bash
# Script triển khai chính - Master Deployment Script
# Chạy từ thư mục gốc của project

cd "$(dirname "$0")"

# Kiểm tra tham số
MODE=${1:-full}

case "$MODE" in
    full|--full|-f)
        echo "🚀 Chạy triển khai toàn diện..."
        ./scripts/deploy-full-update.sh true false
        ;;
    quick|--quick|-q)
        echo "⚡ Chạy triển khai nhanh..."
        shift
        ./scripts/deploy-quick.sh "$@"
        ;;
    clean|--clean|-c)
        echo "🧹 Chạy triển khai với xóa images cũ..."
        ./scripts/deploy-full-update.sh true true
        ;;
    help|--help|-h)
        echo "Cách sử dụng: ./deploy.sh [mode]"
        echo ""
        echo "Modes:"
        echo "  full, -f    Triển khai toàn diện (mặc định)"
        echo "  quick, -q   Triển khai nhanh chỉ rebuild services đã thay đổi"
        echo "  clean, -c   Triển khai toàn diện và xóa images cũ"
        echo "  help, -h    Hiển thị hướng dẫn này"
        echo ""
        echo "Ví dụ:"
        echo "  ./deploy.sh full              # Triển khai toàn diện"
        echo "  ./deploy.sh quick             # Triển khai nhanh tất cả services"
        echo "  ./deploy.sh quick backend     # Chỉ rebuild backend"
        echo "  ./deploy.sh clean             # Triển khai và xóa images cũ"
        ;;
    *)
        echo "❌ Mode không hợp lệ: $MODE"
        echo "Chạy './deploy.sh help' để xem hướng dẫn"
        exit 1
        ;;
esac

