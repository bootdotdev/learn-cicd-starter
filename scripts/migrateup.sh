#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../sql/schema"
echo "Running: goose turso <REDACTED> up"
goose turso "$DATABASE_URL" up
