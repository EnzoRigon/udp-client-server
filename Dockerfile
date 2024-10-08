# Use the official Ubuntu image from the Docker Hub
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    python-is-python3 \
    bison \
    build-essential \
    cmake \
    flex \
    git \
    libedit-dev \
    libllvm11 \
    llvm-11-dev \
    libclang-11-dev \
    zlib1g-dev \
    libelf-dev \
    libfl-dev \
    python3-distutils \
    checkinstall \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and extract BCC source code
RUN wget https://github.com/iovisor/bcc/releases/download/v0.25.0/bcc-src-with-submodule.tar.gz && \
    tar xf bcc-src-with-submodule.tar.gz && \
    cd bcc && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_CMD=python3 .. && \
    make && \
    checkinstall --pkgname=bcc --default && \
    cd /app && \
    rm -rf bcc bcc-src-with-submodule.tar.gz

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Define the default command to run your program
CMD ["/bin/bash"]
