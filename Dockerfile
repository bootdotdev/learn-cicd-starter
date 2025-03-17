# syntax=docker/dockerfile:1

# Build the Go app
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod tidy
RUN go build -o notely .

# Run the Go app
FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/notely .
EXPOSE 8080
CMD ["./notely"]
