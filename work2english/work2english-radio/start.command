#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs
nohup ./start.sh > logs/start.command.log 2>&1 &
echo
echo "Work2English Radio is starting in the background."
echo "Run ./status.sh after a few seconds to check the service status."
