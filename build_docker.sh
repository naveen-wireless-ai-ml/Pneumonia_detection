#!/bin/bash
MODEL_NAME=$(sed -n '/^Selected Model Name,/s/^Selected Model Name,//p' deployment_files/model_info.csv)
if [ -z "$MODEL_NAME" ]; then
    echo "ERROR: Could not read model name from model_info.csv"
    exit 1
fi
echo "Selected model: $MODEL_NAME"

if [ ! -f "models/$MODEL_NAME" ]; then
    echo "ERROR: Model not found: models/$MODEL_NAME"
    exit 1
fi

cp "models/$MODEL_NAME" "deployment_files/best_model.keras"
cd deployment_files

# docker system prune -a --volumes
docker builder prune -af
docker build -t pneumonia-detect-backend-api .
docker stop pneumonia-detect-backend-api 2>/dev/null || true
docker rm pneumonia-detect-backend-api 2>/dev/null || true
# gh codespace ports visibility 7860:public
docker run --name pneumonia-detect-backend-api -p 7860:7860 pneumonia-detect-backend-api
echo 'Run: curl -X POST https://special-acorn-r77p9q6q5vg9hp6gq-7860.app.github.dev/predict -F "file=@<filename>"'
