FROM golang:1.24 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o notely

FROM debian:stable-slim
RUN apt-get update && apt-get install -y ca-certificates
COPY --from=builder /app/notely /usr/bin/notely
CMD ["notely"]
