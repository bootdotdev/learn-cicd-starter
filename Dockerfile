FROM --platform=linux/amd64 debian:stretch-slim

ADD notely /usr/bin/notely

CMD ["notely"]
