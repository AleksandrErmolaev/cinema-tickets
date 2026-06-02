#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Creating management cluster with Kind ==="
kind create cluster --config "${ROOT_DIR}/kind/management-cluster-config.yaml"

echo "=== Installing Cluster API (Docker provider) ==="
clusterctl init --infrastructure docker

echo "=== Waiting for CAPD controllers ==="
kubectl -n capd-system wait --for=condition=available deployment/capd-controller-manager --timeout=5m

echo "=== Management cluster is ready ==="
kubectl cluster-info --context kind-capd-management