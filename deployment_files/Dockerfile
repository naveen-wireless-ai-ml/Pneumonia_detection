# Use a minimal base image with Python 3.13 installed
FROM python:3.13-slim

ENV CUDA_VISIBLE_DEVICES=""

# Set the working directory inside the container to /app
WORKDIR /app

# Copy all files from the deployment_files directory on the host to the container's /app directory
COPY . .

# Install dependencies from the requirements file without using cache to reduce image size
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Define the command to start the application using Gunicorn with 4 worker processes
# - `-w 4`: Uses 4 worker processes for handling requests
# - `-b 0.0.0.0:7860`: Binds the server to port 7860 on all network interfaces
# - `app:app`: Runs the Flask app (assuming `app.py` contains the Flask instance named `app`)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "--timeout", "120", "app:app"]
# NOTE: Disable XSRF protection for easier external access in order to make batch predictions