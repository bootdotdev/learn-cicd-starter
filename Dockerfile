# Use a specific Go version (1.22) as the build environment.
FROM golang:1.22-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy go.mod and go.sum and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the application binary
RUN CGO_ENABLED=0 go build -o server .

# Final stage: create a small, efficient image to run the binary
FROM alpine:latest

# Set the working directory
WORKDIR /app

# Copy the compiled binary from the builder stage
COPY --from=builder /app/server ./server

# Expose the port your application listens on
EXPOSE 8080

# Command to run the application
CMD ["./server"]