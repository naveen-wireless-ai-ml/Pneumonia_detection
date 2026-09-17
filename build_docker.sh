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
docker system prune -a --volumes
cd deployment_files
docker build -t pneumonia-detect-backend-api .
docker run -p 7860:7860 pneumonia-detect-backend-api
echo 'Run: curl -X POST http://localhost:7860/predict -F "file=@<filename>"'