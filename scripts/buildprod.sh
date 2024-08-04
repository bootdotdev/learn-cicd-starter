#!/bin/sh
set -e

# Navigate to the root of the project directory
cd "$(dirname "$0")/.."

# Print the current directory
pwd

# List the contents of the current directory
ls -la

# Build the Go project
go build -o notely ./notely
