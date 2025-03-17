FROM ubuntu:latest

RUN apt-get update && apt-get install -y ca-certificates

ADD /notely.exe /usr/bin/notely

CMD ["./notely.exe"]
