#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 radio_service.py status
