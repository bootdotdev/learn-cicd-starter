#!/bin/bash

if [ -f .env ]; then
    source .env
fi

goose turso "$DATABASE_URL" up -dir sql/schema
