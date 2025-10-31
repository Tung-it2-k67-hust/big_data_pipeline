#!/bin/bash
# Verify the deployment and check the status of all components

set -e

echo "Checking Big Data Pipeline Status..."
echo ""

# Check namespace
echo "=== Namespace ==="
kubectl get namespace big-data-pipeline 2>/dev/null || echo "Namespace not found"
echo ""

# Check pods
echo "=== Pods ==="
kubectl get pods -n big-data-pipeline 2>/dev/null || echo "No pods found"
echo ""

# Check services
echo "=== Services ==="
kubectl get svc -n big-data-pipeline 2>/dev/null || echo "No services found"
echo ""

# Check statefulsets
echo "=== StatefulSets ==="
kubectl get statefulsets -n big-data-pipeline 2>/dev/null || echo "No statefulsets found"
echo ""

# Check deployments
echo "=== Deployments ==="
kubectl get deployments -n big-data-pipeline 2>/dev/null || echo "No deployments found"
echo ""

# Check PVCs
echo "=== Persistent Volume Claims ==="
kubectl get pvc -n big-data-pipeline 2>/dev/null || echo "No PVCs found"
echo ""

echo "Status check complete!"
