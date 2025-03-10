#!/bin/bash

GOOS=linux GOARCH=arm64 go build -o notely .
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o notely
