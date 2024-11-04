FROM debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates

ADD notely /usr/bin/notely

COPY .env .env
CMD ["notely"]
