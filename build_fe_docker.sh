#!/bin/bash
cd frontend_files
# docker system prune -a --volumes
docker builder prune -af
docker build -t pneumonia-detect-api .
# Stop and remove existing container after successful build
docker stop pneumonia-detect-api 2>/dev/null || true
docker rm pneumonia-detect-api 2>/dev/null || true
docker run --name pneumonia-detect-api -p 8501:8501 pneumonia-detect-api