#!/bin/bash
set -e

export KUBECONFIG=./kubeconfig-workload.yaml

echo "Current worker nodes:"
kubectl get nodes -l "!node-role.kubernetes.io/control-plane"

echo "Creating a deployment that requires more CPU than available on one node..."
kubectl delete deployment load-generator --ignore-not-found
kubectl create deployment load-generator --image=polinux/stress
kubectl set resources deployment load-generator --requests=cpu=2 --limits=cpu=2
kubectl scale deployment load-generator --replicas=3

echo "Waiting for pods to become pending (scale-up trigger)..."
sleep 15

echo "Cluster Autoscaler should add a new worker node soon."
echo "Monitor nodes with: kubectl get nodes -w"
echo "Monitor CA logs: kubectl -n kube-system logs deployment/cluster-autoscaler -f"

sleep 120
echo "Current nodes after scale-up:"
kubectl get nodes -o wide

read -p "Press Enter to delete load and watch scale-down..."
kubectl delete deployment load-generator
echo "Load removed. Watch nodes scale down in ~10 minutes (scale-down-delay-after-add=5m)."