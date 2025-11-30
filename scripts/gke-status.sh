#!/bin/bash
# =============================================================================
# Script: gke-status.sh
# Mô tả: Kiểm tra trạng thái của Big Data Pipeline trên GKE
# Cách dùng: ./scripts/gke-status.sh
# =============================================================================

set -e

NAMESPACE="big-data-pipeline"

echo "=============================================="
echo "📊 Trạng thái Big Data Pipeline trên GKE"
echo "=============================================="
echo ""

# Kiểm tra namespace
if ! kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
    echo "❌ Namespace '$NAMESPACE' không tồn tại"
    echo "   Chạy: ./scripts/gke-deploy.sh để deploy"
    exit 1
fi

echo "📋 Tất cả Pods:"
echo "----------------"
kubectl get pods -n $NAMESPACE -o wide
echo ""

echo "🌐 Services (với External IPs):"
echo "--------------------------------"
kubectl get services -n $NAMESPACE
echo ""

echo "💾 PersistentVolumeClaims:"
echo "--------------------------"
kubectl get pvc -n $NAMESPACE
echo ""

echo "📈 Resource Usage:"
echo "------------------"
kubectl top pods -n $NAMESPACE 2>/dev/null || echo "(Metrics server chưa được cài đặt)"
echo ""

# Kiểm tra health của từng service
echo "=============================================="
echo "🏥 Health Check từng Service"
echo "=============================================="

# Zookeeper
echo ""
echo "🐘 Zookeeper:"
ZOOKEEPER_POD=$(kubectl get pod -n $NAMESPACE -l app=zookeeper -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$ZOOKEEPER_POD" ]; then
    STATUS=$(kubectl get pod $ZOOKEEPER_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
    READY=$(kubectl get pod $ZOOKEEPER_POD -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    echo "   Pod: $ZOOKEEPER_POD | Status: $STATUS | Ready: $READY"
else
    echo "   ❌ Không tìm thấy pod"
fi

# Kafka
echo ""
echo "📨 Kafka:"
KAFKA_POD=$(kubectl get pod -n $NAMESPACE -l app=kafka -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$KAFKA_POD" ]; then
    STATUS=$(kubectl get pod $KAFKA_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
    READY=$(kubectl get pod $KAFKA_POD -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    echo "   Pod: $KAFKA_POD | Status: $STATUS | Ready: $READY"
else
    echo "   ❌ Không tìm thấy pod"
fi

# Elasticsearch
echo ""
echo "🔍 Elasticsearch:"
ES_POD=$(kubectl get pod -n $NAMESPACE -l app=elasticsearch -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$ES_POD" ]; then
    STATUS=$(kubectl get pod $ES_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
    READY=$(kubectl get pod $ES_POD -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    echo "   Pod: $ES_POD | Status: $STATUS | Ready: $READY"
else
    echo "   ❌ Không tìm thấy pod"
fi

# Cassandra
echo ""
echo "💾 Cassandra:"
CASS_POD=$(kubectl get pod -n $NAMESPACE -l app=cassandra -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$CASS_POD" ]; then
    STATUS=$(kubectl get pod $CASS_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
    READY=$(kubectl get pod $CASS_POD -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    echo "   Pod: $CASS_POD | Status: $STATUS | Ready: $READY"
else
    echo "   ❌ Không tìm thấy pod"
fi

# Kafka Producer
echo ""
echo "📤 Kafka Producer:"
kubectl get pods -n $NAMESPACE -l app=kafka-producer -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,READY:.status.conditions[?(@.type=="Ready")].status' 2>/dev/null || echo "   ❌ Không tìm thấy"

# Spark Streaming
echo ""
echo "⚡ Spark Streaming:"
kubectl get pods -n $NAMESPACE -l app=spark-streaming -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,READY:.status.conditions[?(@.type=="Ready")].status' 2>/dev/null || echo "   ❌ Không tìm thấy"

# Streamlit
echo ""
echo "📈 Streamlit:"
kubectl get pods -n $NAMESPACE -l app=streamlit -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,READY:.status.conditions[?(@.type=="Ready")].status' 2>/dev/null || echo "   ❌ Không tìm thấy"

# Kibana
echo ""
echo "📊 Kibana:"
kubectl get pods -n $NAMESPACE -l app=kibana -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,READY:.status.conditions[?(@.type=="Ready")].status' 2>/dev/null || echo "   ❌ Không tìm thấy"

# Prometheus
echo ""
echo "📉 Prometheus:"
kubectl get pods -n $NAMESPACE -l app=prometheus -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,READY:.status.conditions[?(@.type=="Ready")].status' 2>/dev/null || echo "   ❌ Không tìm thấy"

# Grafana
echo ""
echo "📉 Grafana:"
kubectl get pods -n $NAMESPACE -l app=grafana -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,READY:.status.conditions[?(@.type=="Ready")].status' 2>/dev/null || echo "   ❌ Không tìm thấy"

echo ""
echo "=============================================="
echo "🌐 URLs để truy cập (nếu có External IP)"
echo "=============================================="
KIBANA_IP=$(kubectl get svc kibana -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
STREAMLIT_IP=$(kubectl get svc streamlit -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
GRAFANA_IP=$(kubectl get svc grafana -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
PROMETHEUS_IP=$(kubectl get svc prometheus -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

if [ -n "$KIBANA_IP" ]; then
    echo "   Kibana: http://$KIBANA_IP:5601"
else
    echo "   Kibana: <pending> - dùng port-forward: kubectl port-forward svc/kibana 5601:5601 -n $NAMESPACE"
fi

if [ -n "$STREAMLIT_IP" ]; then
    echo "   Streamlit: http://$STREAMLIT_IP:8501"
else
    echo "   Streamlit: <pending> - dùng port-forward: kubectl port-forward svc/streamlit 8501:8501 -n $NAMESPACE"
fi

if [ -n "$GRAFANA_IP" ]; then
    echo "   Grafana: http://$GRAFANA_IP:3000 (admin/admin)"
else
    echo "   Grafana: <pending> - dùng port-forward: kubectl port-forward svc/grafana 3000:3000 -n $NAMESPACE"
fi

if [ -n "$PROMETHEUS_IP" ]; then
    echo "   Prometheus: http://$PROMETHEUS_IP:9090"
else
    echo "   Prometheus: <pending> - dùng port-forward: kubectl port-forward svc/prometheus 9090:9090 -n $NAMESPACE"
fi

echo ""
