#!/bin/bash
set -e

echo "Applying DestinationRules..."
kubectl apply -f istio/destinationrule/destinationrule-auth.yaml
kubectl apply -f istio/destinationrule/destinationrule-movie.yaml
kubectl apply -f istio/destinationrule/destinationrule-booking.yaml
kubectl apply -f istio/destinationrule/destinationrule-payment.yaml
kubectl apply -f istio/destinationrule/destinationrule-analytics.yaml
kubectl apply -f istio/destinationrule/destinationrule-notification.yaml

echo "Applying VirtualServices (internal)..."
kubectl apply -f istio/virtualservice/virtualservice-auth.yaml
kubectl apply -f istio/virtualservice/virtualservice-movie.yaml
kubectl apply -f istio/virtualservice/virtualservice-booking.yaml
kubectl apply -f istio/virtualservice/virtualservice-payment.yaml
kubectl apply -f istio/virtualservice/virtualservice-analytics.yaml
kubectl apply -f istio/virtualservice/virtualservice-notification.yaml

echo "Applying Gateway and external VirtualService..."
kubectl apply -f istio/gateway.yaml

echo "Istio configurations applied successfully."