FROM golang:1.27.3-alpine3.24 AS builder

WORKDIR /usr/src/app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -v -o /usr/local/bin/app .

FROM alpine:3.24

ENV PORT=8080
EXPOSE 8080

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.1.0 /lambda-adapter /opt/extensions/lambda-adapter
COPY --from=builder /usr/local/bin/app /notely

CMD ["/notely"]
