#!/bin/bash

# Navigate to the project's root directory (if not already there)
cd "$(dirname "$0")/.."

# Ensure the directory structure is as expected
ls -R

# Build the project
go build -o cmd/notely ./cmd/notely
