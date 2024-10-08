# Use the official Ubuntu image from the Docker Hub
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    software-properties-common \
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
    clang \
    checkinstall \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add the BCC repository and install BCC tools
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4052245BD4284CDD && \
    echo "deb https://repo.iovisor.org/apt/$(lsb_release -cs) $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/iovisor.list && \
    apt-get update && \
    apt-get install -y bcc-tools libbcc-examples linux-headers-$(uname -r)

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Define the default command to run your program
CMD ["/bin/bash"]
