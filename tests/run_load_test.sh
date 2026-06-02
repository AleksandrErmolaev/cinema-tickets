#!/bin/bash

set -e

GATEWAY_URL="${GATEWAY_URL:-http://localhost:80}"

echo "Запуск Locust против $GATEWAY_URL"
echo "Откройте http://localhost:8089 для управления тестом"

locust -f locustfile.py --host=$GATEWAY_URL --web-port=8089