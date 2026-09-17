#!/bin/bash
cd frontend_files
# Stop and remove existing container if it is running
docker build -t pneumonia-detect-api .
docker stop pneumonia-detect-api 2>/dev/null || true
docker rm pneumonia-detect-api 2>/dev/null || true
gh codespace ports visibility 8501:public
docker run --name pneumonia-detect-api -p 8501:8501 pneumonia-detect-api