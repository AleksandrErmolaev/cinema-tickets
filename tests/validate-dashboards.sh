#!/bin/bash
set -e

export KUBECONFIG="${KUBECONFIG:-./kubeconfig-workload.yaml}"

GRAFANA_POD=$(kubectl get pod -n observability -l app=grafana -o jsonpath='{.items[0].metadata.name}')
if [ -z "$GRAFANA_POD" ]; then
    echo "Grafana pod not found"
    exit 1
fi

kubectl port-forward -n observability $GRAFANA_POD 3000:3000 &
PF_PID=$!
sleep 5

GRAFANA_URL="http://localhost:3000"
ADMIN_PASS="admin"

echo "=== Проверка дашбордов Grafana ==="
DASHBOARDS=$(curl -s -u admin:$ADMIN_PASS $GRAFANA_URL/api/search | jq -r '.[].uid')

if echo "$DASHBOARDS" | grep -q "microservices-overview"; then
    echo "Дашборд 'Microservices Overview' найден"
else
    echo "Дашборд 'Microservices Overview' не найден"
fi

if echo "$DASHBOARDS" | grep -q "kafka-dashboard"; then
    echo "Дашборд 'Kafka Dashboard' найден"
else
    echo "Дашборд 'Kafka Dashboard' не найден"
fi

if echo "$DASHBOARDS" | grep -q "istio-mesh-dashboard"; then
    echo "Дашборд 'Istio Mesh Dashboard' найден"
else
    echo "Дашборд 'Istio Mesh Dashboard' не найден"
fi

echo "=== Проверка метрик через VictoriaMetrics ==="
VM_SELECT_POD=$(kubectl get pod -n observability -l app=victoria-metrics-vmselect -o jsonpath='{.items[0].metadata.name}')
if [ -n "$VM_SELECT_POD" ]; then
    kubectl port-forward -n observability $VM_SELECT_POD 8481:8481 &
    PF_VM_PID=$!
    sleep 3
    
    LAG_METRIC=$(curl -s "http://localhost:8481/select/0/prometheus/api/v1/query?query=kafka_consumer_lag" | jq -r '.data.result | length')
    if [ "$LAG_METRIC" -gt 0 ]; then
        echo "Метрика kafka_consumer_lag найдена"
    else
        echo "Метрика kafka_consumer_lag не найдена (возможно, нет активных consumer)"
    fi
    
    RATE_LIMIT_METRIC=$(curl -s "http://localhost:8481/select/0/prometheus/api/v1/query?query=envoy_http_ratelimit_http_local_rate_limit_enforced" | jq -r '.data.result | length')
    if [ "$RATE_LIMIT_METRIC" -gt 0 ]; then
        echo "Метрика rate limiter найдена"
    else
        echo "Метрика rate limiter не найдена (возможно, не было превышения лимита)"
    fi
    
    kill $PF_VM_PID 2>/dev/null
else
    echo "VictoriaMetrics vmselect не найден, проверка метрик пропущена"
fi

kill $PF_PID 2>/dev/null

echo "=== Валидация завершена ==="