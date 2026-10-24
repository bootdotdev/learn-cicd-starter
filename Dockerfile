# Stage 1: Build AWS Lambda Web Adapter
FROM rust:1-alpine3.24 AS adapter-builder

RUN apk add --no-cache \
    build-base \
    cmake \
    perl \
    curl \
    ca-certificates

WORKDIR /usr/src/adapter

ARG ADAPTER_VERSION=v1.1.0

RUN curl -fsSL \
    "https://github.com/aws/aws-lambda-web-adapter/archive/refs/tags/${ADAPTER_VERSION}.tar.gz" \
    -o adapter.tar.gz \
    && tar -xzf adapter.tar.gz --strip-components=1 \
    && rm adapter.tar.gz

# Use Alpine's GCC as the musl linker
ENV CARGO_TARGET_X86_64_UNKNOWN_LINUX_MUSL_LINKER=gcc

RUN rustup target add x86_64-unknown-linux-musl
RUN cargo build \
    --release \
    --locked \
    --target x86_64-unknown-linux-musl \
    --bin lambda-adapter

# Stage 2: Build Go application
FROM golang:1.27.3-alpine3.24 AS builder

WORKDIR /usr/src/app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -v -o /usr/local/bin/app .

# Stage 3: Runtime
FROM alpine:3.24

ENV PORT=8080
EXPOSE 8080

COPY --from=adapter-builder \
    /usr/src/adapter/target/x86_64-unknown-linux-musl/release/lambda-adapter \
    /opt/extensions/lambda-adapter

COPY --from=builder /usr/local/bin/app /notely

CMD ["/notely"]
