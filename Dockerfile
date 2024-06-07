# Use a smaller base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN apk update && apk add --no-cache \
    aws-cli \
    ffmpeg \
    libsm6 \
    libxext6 \
    unzip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-dependencies && \
    rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD ["python3", "app.py"]
