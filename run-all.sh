#!/bin/bash
# Wrapper script để chạy toàn bộ quy trình build và deploy
# Chạy từ thư mục gốc của project

cd "$(dirname "$0")"
exec ./scripts/run-all.sh "$@"

