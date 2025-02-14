ARG PLATFORM=linux/amd64
FROM --platform=$PLATFORM debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates

ADD notely /usr/bin/notely

CMD ["notely"]
