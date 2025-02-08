FROM debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates file

ADD notely /usr/bin/notely

# Debug lines
RUN file /usr/bin/notely
RUN chmod +x /usr/bin/notely
RUN ls -l /usr/bin/notely

CMD ["notely"]