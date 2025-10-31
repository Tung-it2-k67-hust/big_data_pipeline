.PHONY: help build deploy status cleanup docker-up docker-down

help:
	@echo "Big Data Pipeline - Available Commands:"
	@echo "  make build         - Build all Docker images"
	@echo "  make deploy        - Deploy to Kubernetes"
	@echo "  make status        - Check deployment status"
	@echo "  make cleanup       - Clean up Kubernetes resources"
	@echo "  make docker-up     - Start services with Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make docker-logs   - Show Docker Compose logs"

build:
	@echo "Building Docker images..."
	./scripts/build-images.sh

deploy:
	@echo "Deploying to Kubernetes..."
	./scripts/deploy.sh

status:
	@echo "Checking deployment status..."
	./scripts/status.sh

cleanup:
	@echo "Cleaning up resources..."
	./scripts/cleanup.sh

docker-up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker Compose services..."
	docker-compose down

docker-logs:
	@echo "Showing Docker Compose logs..."
	docker-compose logs -f
