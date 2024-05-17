# Dockerize a python app
FROM python:3.11.8-slim

# Create app directory
WORKDIR /app

# Install requirements
COPY requirements.txt task/req.txt ./
RUN apt-get update && \
    python -m pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    pip install -r req.txt --no-cache-dir && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#Copy app
COPY . .

# Run app
ENTRYPOINT ["/bin/sh", "-c", \
    "python task/generate_bin.py && \
    exec uvicorn main:app --host 0.0.0.0 --port 8000"]
