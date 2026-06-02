#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

export KUBECONFIG="${ROOT_DIR}/kubeconfig-workload.yaml"

echo "=== Applying autoscaler annotations to MachineDeployment ==="
kubectl apply -f "${ROOT_DIR}/cluster-api/machine-deployment-autoscaler.yaml"

helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm repo update

helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler \
  --namespace kube-system \
  --values "${ROOT_DIR}/cluster-api/cluster-autoscaler-values.yaml"

echo "=== Waiting for Cluster Autoscaler ==="
kubectl -n kube-system rollout status deployment/cluster-autoscaler --timeout=2m

echo "=== Cluster Autoscaler is ready ==="
kubectl get nodes