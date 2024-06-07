# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
RUN apt update -y && apt install awscli -y

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 unzip -y && pip install -r requirements.txt

# Install dependencies for OpenCV
# RUN apt-get update && \
#     apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["python3", "app.py"]