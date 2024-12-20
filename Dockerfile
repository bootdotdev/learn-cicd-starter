FROM --platform=linux/amd64 debian:stable-slim
RUN apt-get update && \
    apt-get install -y \
    ca-certificates \
    wget \
    build-essential \
    dos2unix \
    golang-go 

ADD notely /usr/bin/
RUN /usr/bin/buildprod.sh
CMD ["/usr/bin/notely"]
