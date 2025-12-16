#!/bin/bash

# Wrapper script for data anomaly detection
# This exists to match the naming in the data plan
# and delegates to the core implementation in detect-anomalies.sh.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/detect-anomalies.sh" "$@"

