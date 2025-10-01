#!/bin/bash

# Build dell'immagine (inclusi tutti i file)
docker build -t metimeter .

# Esegui il container con:
# - Port mapping
# - Volume per i file persistenti (uploads e output)
docker run -p 5001:5001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/HAIIAssessment/static:/app/HAIIAssessment/static \
  -v $(pwd)/HAIIAssessment/uploads:/app/HAIIAssessment/uploads \
  metimeter