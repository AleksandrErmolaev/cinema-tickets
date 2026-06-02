#!/bin/bash
set -e

export KUBECONFIG=./kubeconfig-workload.yaml

helm repo add cilium https://helm.cilium.io/
helm repo update

helm upgrade --install cilium cilium/cilium \
  --namespace kube-system \
  --values cilium/cilium-values-workload.yaml

echo "Waiting for Cilium on workload cluster..."
kubectl -n kube-system rollout status ds/cilium --timeout=5m