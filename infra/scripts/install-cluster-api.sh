#!/bin/bash
set -e

echo "Installing Cluster API and Docker provider..."
clusterctl init --infrastructure docker

echo "Waiting for CAPD controllers..."
kubectl -n capd-system wait --for=condition=available deployment/capd-controller-manager --timeout=5m