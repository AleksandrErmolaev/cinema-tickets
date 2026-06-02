#!/bin/bash

set -e

SERVICE_TO_FAIL=${1:-"payment-service"}   # можно передать другие сервисы
NAMESPACE=${2:-"payment"}

echo "=== Проверка Circuit Breaker для $SERVICE_TO_FAIL в namespace $NAMESPACE ==="

echo "1. Проверка доступности сервиса..."
kubectl get pods -n $NAMESPACE | grep $SERVICE_TO_FAIL

echo "2. Отключаем сервис (replicas=0)..."
kubectl scale deployment $SERVICE_TO_FAIL -n $NAMESPACE --replicas=0

echo "   Ждём 10 секунд..."
sleep 10

echo "3. Запускаем нагрузку на Ingress Gateway (для триггера Circuit Breaker)..."
GATEWAY_URL="${GATEWAY_URL:-http://192.168.56.100:80}"
ENDPOINT=""
case $SERVICE_TO_FAIL in
  "payment-service")
    ENDPOINT="/payments"
    DATA='{"booking_id":"test-cb","amount":10.0}'
    ;;
  "booking-service")
    ENDPOINT="/bookings"
    DATA='{"session_id":"test","seat_numbers":[1],"user_id":"test"}'
    ;;
  "auth-service")
    ENDPOINT="/profile"
    DATA=""
    ;;
  *)
    echo "Неизвестный сервис, пропускаем автоматическую нагрузку"
    ;;
esac

if [ -n "$ENDPOINT" ]; then
  for i in {1..10}; do
    if [ -n "$DATA" ]; then
      curl -s -X POST $GATEWAY_URL$ENDPOINT -H "Content-Type: application/json" -d "$DATA" > /dev/null || true
    else
      curl -s $GATEWAY_URL$ENDPOINT > /dev/null || true
    fi
    echo -n "."
  done
  echo ""
fi

echo "4. Проверка состояния Circuit Breaker (логи pilot, метрики envoy)..."
echo "   Смотрим логи Istio Pilot:"
kubectl logs -n istio-system deployment/istiod --tail=50 | grep -i "circuit" || echo "   (нет соответствующих логов)"

echo "   Метрики Envoy в sidecar:"
POD=$(kubectl get pod -n $NAMESPACE -l app=$SERVICE_TO_FAIL --field-selector=status.phase=Running -o name 2>/dev/null | head -1)
if [ -n "$POD" ]; then
  kubectl exec $POD -n $NAMESPACE -c istio-proxy -- curl -s localhost:15000/stats | grep -E "circuit_breakers|upstream_rq_pending_overflow" | head -10
else
  echo "   (нет работающих подов для извлечения метрик)"
fi

echo "5. Восстанавливаем сервис (replicas=1)..."
kubectl scale deployment $SERVICE_TO_FAIL -n $NAMESPACE --replicas=1

echo "=== Завершено ==="
echo "Для визуализации Circuit Breaker откройте Kiali: kubectl port-forward -n istio-system svc/kiali 20001:20001"