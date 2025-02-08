FROM debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates file

WORKDIR /app
COPY notely .

RUN chmod +x notely

EXPOSE 8080
ENV PORT=8080

CMD ["./notely"]