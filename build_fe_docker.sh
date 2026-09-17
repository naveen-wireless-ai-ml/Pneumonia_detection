#!/bin/bash
cd frontend_files
docker build -t pneumonia-detect-api .
docker run -p 8501:8501 pneumonia-detect-api
