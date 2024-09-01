FROM ubuntu:latest

RUN apt-get update && apt-get install -y ca-certificates

WORKDIR /
ADD notely /usr/bin/notely

CMD ["notely"]
