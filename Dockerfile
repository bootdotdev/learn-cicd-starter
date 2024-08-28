FROM ubuntu:latest

# Install necessary packages and clean up
RUN apt-get update && apt-get install -y ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory and copy the notely binary
WORKDIR /usr/bin
COPY notely /usr/bin/notely

# Ensure binary has execute permissions
RUN chmod +x /usr/bin/notely

# Command to run the application
CMD ["notely"]
