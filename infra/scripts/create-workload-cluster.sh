#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Applying workload cluster manifest ==="
kubectl apply -f "${ROOT_DIR}/cluster-api/workload-cluster.yaml"

echo "=== Waiting for workload cluster to be provisioned (2-3 minutes) ==="
sleep 10
while ! clusterctl get kubeconfig workload > "${ROOT_DIR}/kubeconfig-workload.yaml" 2>/dev/null; do
  echo "Waiting for workload cluster kubeconfig..."
  sleep 5
done

export KUBECONFIG="${ROOT_DIR}/kubeconfig-workload.yaml"
echo "=== Waiting for workload cluster nodes ==="
while ! kubectl get nodes 2>/dev/null | grep -q "Ready"; do
  echo "Waiting for nodes..."
  sleep 5
done

echo "=== Installing Cilium CNI on workload cluster ==="
"${SCRIPT_DIR}/install-cilium-workload.sh"

echo "=== Workload cluster is ready with Cilium ==="
kubectl get nodes -o wide