#!/bin/bash
# Script deploy Kafka KRaft trên GKE và test

set -e

echo "🚀 Bước 1: Deploy Kafka KRaft cluster..."
kubectl apply -f kafka-kraft.yaml

echo "⏳ Bước 2: Theo dõi pods Kafka (chờ đến khi Running hết)..."
kubectl get pods -n kafka -w

# Sau khi pods Running, chạy tiếp
echo "✅ Pods đã Running. Bước 3: Kiểm tra services..."
kubectl get svc -n kafka

echo "📋 Bước 4: Lấy EXTERNAL-IP (copy IP này để dùng trong Python)..."
kubectl get svc my-cluster-kafka-external-bootstrap -n kafka -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

echo "💡 Bước 5: Hướng dẫn chạy test Python (thay EXTERNAL_IP trong consumer.py):"
echo "  - Mở terminal mới, cd vào kafka-producer/src/"
echo "  - Chạy producer: python producer.py"
echo "  - Chạy consumer: python consumer.py (nhớ sửa EXTERNAL_IP trong file)"

echo "🎉 Hoàn thành! Nếu cần, chạy lại script này nếu lỗi."