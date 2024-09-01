FROM ubuntu:latest

RUN apt-get update && apt-get install -y ca-certificates

WORKDIR /
ADD notely /usr/bin/notely
EXPOSE 8080

CMD ["notely"]
