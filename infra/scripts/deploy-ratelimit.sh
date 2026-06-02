#!/bin/bash
set -e

echo "Deploying Redis for rate limiting..."
kubectl apply -f rate-limit/redis-ratelimit.yaml

echo "Deploying Envoy Rate Limit service..."
kubectl apply -f rate-limit/ratelimit-config.yaml
kubectl apply -f rate-limit/ratelimit-deployment.yaml

echo "Applying EnvoyFilter for rate limiting on Ingress Gateway..."
kubectl apply -f rate-limit/envoy-filter.yaml

echo "Rate limiting deployed successfully."