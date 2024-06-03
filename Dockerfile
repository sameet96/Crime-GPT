FROM python:3.9

# Install dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the entire yolov3 directory
COPY yolov3 /app/yolov3

COPY . .

# Set environment variables from build arguments
ARG OPEN_AI_KEY
ENV OPEN_AI_KEY=$OPEN_AI_KEY

# Expose the port
EXPOSE $PORT

CMD ["sh", "-c", "gunicorn --workers=4 --bind 0.0.0.0:$PORT app:app"]