#!/bin/bash

# Start all services
docker compose --profile init up -d

# Wait for Ollama service to be ready
echo "Waiting for Ollama service to be ready..."
while ! docker compose exec -T ollama ollama list 2>/dev/null; do
    sleep 5
done

# Pull the phi3 model
echo "Pulling phi3 model..."
docker compose exec -T ollama ollama pull phi3

echo "Startup complete!"