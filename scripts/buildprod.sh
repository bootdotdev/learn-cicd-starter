#!/bin/sh
set -e

# Navigate to the root of the project directory
cd "$(dirname "$0")/.."

# Build the Go project
go build -o notely
