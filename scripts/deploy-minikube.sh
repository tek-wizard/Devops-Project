#!/usr/bin/env bash
# One-shot local deployment: build images, load them into minikube,
# and install the Helm chart. Run from the repo root.
set -euo pipefail

echo "==> Building images"
docker build -t deskflow-backend:local ./backend
docker build -t deskflow-frontend:local ./frontend

echo "==> Starting minikube (if not already running)"
minikube status >/dev/null 2>&1 || minikube start --driver=docker --cpus=4 --memory=4096
minikube addons enable ingress
minikube addons enable metrics-server

echo "==> Loading images into minikube"
minikube image load deskflow-backend:local
minikube image load deskflow-frontend:local

echo "==> Creating namespace + installing chart"
kubectl apply -f k8s/namespace.yaml
# ServiceMonitor is enabled only if the Prometheus Operator CRDs exist.
if kubectl get crd servicemonitors.monitoring.coreos.com >/dev/null 2>&1; then
  SM=true
else
  SM=false
  echo "    (Prometheus Operator not found; installing chart with serviceMonitor disabled)"
fi
helm upgrade --install deskflow helm/deskflow -n deskflow --set serviceMonitor.enabled=$SM

echo "==> Waiting for rollouts"
kubectl -n deskflow rollout status deploy/deskflow-postgres
kubectl -n deskflow rollout status deploy/deskflow-backend
kubectl -n deskflow rollout status deploy/deskflow-frontend

echo "==> Done. Pods:"
kubectl -n deskflow get pods

cat <<'EOF'

To reach the app locally:
  echo "$(minikube ip) deskflow.local" | sudo tee -a /etc/hosts
  # then open http://deskflow.local
Or without editing hosts:
  kubectl -n deskflow port-forward svc/deskflow-frontend 8080:80
  # then open http://localhost:8080
EOF
