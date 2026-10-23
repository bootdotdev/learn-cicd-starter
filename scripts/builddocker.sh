#!/bin/bash

docker buildx build \
  --platform=linux/amd64 \
  --pull \
  -t "${DOCKERHUB_NAMESPACE:?"ERROR: DOCKERHUB_NAMESPACE environment variable is not set or empty"}/notely:latest" \
  .
