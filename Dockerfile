FROM debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates file

WORKDIR /app
COPY notely .

RUN chmod +x notely

EXPOSE 8080
ENV PORT=8080

# Be explicit about listening on all interfaces
ENV HOST=0.0.0.0
CMD ["./notely"]