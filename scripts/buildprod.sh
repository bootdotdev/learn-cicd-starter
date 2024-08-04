#!/bin/sh
go mod tidy
go build -o notely ./cmd/notely
