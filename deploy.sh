#!/bin/bash

# Stop execution on error
set -e

# Variable definitions
ZONE="us-east1-b"
VM_NAME="my-docker-vm"
PROJECT="estudos-444305"
REMOTE_PATH="port-reminder"

# Function to display messages
log() {
  echo "[INFO] $1"
}

# Check if gcloud is installed
if ! command -v gcloud &>/dev/null; then
  echo "[ERROR] gcloud not found! Please install Google Cloud SDK."
  exit 1
fi

log "Starting deployment on VM $VM_NAME..."

# Execute commands on the remote machine via SSH
gcloud compute ssh --zone "$ZONE" "$VM_NAME" --project "$PROJECT" --command \
  "cd $REMOTE_PATH && \
 git pull && \
 sudo docker-compose up -d --build"

log "Deployment completed successfully!"
