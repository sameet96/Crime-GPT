FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    yasm \
    pkg-config \
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk2.0-dev \
    libatlas-base-dev \
    gfortran \
    python3-dev \
    python3-pip

# Install OpenCV from source
RUN pip install numpy
RUN git clone https://github.com/opencv/opencv.git && \
    git clone https://github.com/opencv/opencv_contrib.git && \
    cd opencv && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
          -D PYTHON_EXECUTABLE=/usr/bin/python3 \
          -D BUILD_EXAMPLES=ON .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd ../.. && \
    rm -rf opencv opencv_contrib

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