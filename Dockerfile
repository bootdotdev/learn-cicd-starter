# syntax=docker/dockerfile:1

############# Build stage #############
FROM golang:1.22-alpine AS builder
WORKDIR /app

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source files
COPY . .

# Build a static Linux binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /app/notely .

############# Runtime stage #############
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app/notely /usr/local/bin/notely

USER nonroot:nonroot
ENTRYPOINT ["/usr/local/bin/notely"]

