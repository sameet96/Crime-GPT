FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0

# Install OpenCV using pip
RUN pip install numpy opencv-python-headless

# Create working directory
WORKDIR /app

# Copy requirement files
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the yolov3 directory
COPY yolov3 /app/yolov3

# Copy the entire project
COPY . .

# Expose the port
EXPOSE $PORT

# Run the application
CMD ["sh", "-c", "gunicorn --workers=4 --bind 0.0.0.0:$PORT app:app"]