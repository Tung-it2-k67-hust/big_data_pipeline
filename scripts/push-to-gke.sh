#!/bin/bash
# Script tự động build và push images lên Google Artifact Registry bằng Cloud Build

set -e

# Cấu hình
PROJECT_ID="robust-magpie-479807-f1"
REGION="asia-northeast1"
REPO_NAME="my-repo"

echo "🚀 Bắt đầu quá trình Build & Push bằng Cloud Build..."

# 1. Bật Cloud Build API
echo "🔧 Bật Cloud Build API..."
gcloud services enable cloudbuild.googleapis.com

# 2. Tạo repository nếu chưa có
echo "📦 Kiểm tra/Tạo Artifact Registry..."
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Big Data Pipeline" || true

# 3. Build & Push Kafka Producer bằng Cloud Build
echo "🏗️ Building Kafka Producer bằng Cloud Build..."
cd kafka-producer
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID .
cd ..

# 4. Build & Push Spark Streaming bằng Cloud Build
echo "🏗️ Building Spark Streaming bằng Cloud Build..."
cd spark-streaming
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID .
cd ..

# 5. Build & Push Streamlit Dashboard bằng Cloud Build
echo "🏗️ Building Streamlit Dashboard bằng Cloud Build..."
cd streamlit-dashboard
gcloud builds submit --config=cloudbuild.yaml --substitutions=_PROJECT_ID=$PROJECT_ID .
cd ..

echo "✅ Hoàn thành! Tất cả images đã được build và push lên Google Cloud Build."
echo "📋 Kiểm tra images:"
echo "gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME --include-tags"
