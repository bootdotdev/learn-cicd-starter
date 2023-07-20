FROM --platform=linux/amd64 debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates

ADD notely /usr/bin/notely

RUN gcloud builds submit --tag us-central1-docker.pkg.dev/notely-393407/notely-ar-repo/1.0 .

CMD ["notely"]
