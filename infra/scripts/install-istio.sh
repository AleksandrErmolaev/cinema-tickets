#!/bin/bash
set -e

echo "Downloading Istio 1.21.0..."
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.21.0 sh -
cd istio-1.21.0
export PATH=$PWD/bin:$PATH

echo "Installing Istio with demo profile..."
istioctl install --set profile=demo -y

echo "Enabling automatic sidecar injection for namespaces: auth, movie, booking, payment, analytics, notification, kafka"
kubectl label namespace auth istio-injection=enabled --overwrite
kubectl label namespace movie istio-injection=enabled --overwrite
kubectl label namespace booking istio-injection=enabled --overwrite
kubectl label namespace payment istio-injection=enabled --overwrite
kubectl label namespace analytics istio-injection=enabled --overwrite
kubectl label namespace notification istio-injection=enabled --overwrite
kubectl label namespace kafka istio-injection=enabled --overwrite

echo "Installing addons: Kiali, Prometheus, Grafana (optional)"
kubectl apply -f samples/addons/kiali.yaml
kubectl apply -f samples/addons/prometheus.yaml

echo "Waiting for Istio Ingress Gateway..."
kubectl -n istio-system rollout status deployment/istio-ingressgateway --timeout=5m

echo "Istio installed successfully"