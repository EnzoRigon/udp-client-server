FROM ubuntu:bionic-20210325

ENV PATH /usr/share/bcc/tools:$PATH

# Update sources
RUN sed -i "s#deb http://deb.debian.org/debian buster main#deb http://deb.debian.org/debian buster main contrib non-free#g" /etc/apt/sources.list

# Install essential tools and libraries
RUN apt-get update && apt-get install -y \
    ca-certificates \
    clang \
    curl \
    gcc \
    git \
    g++ \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    python3-pip \
    python3-setuptools \
    build-essential \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    debhelper \
    cmake \
    libllvm3.9 \
    llvm-dev \
    libclang-dev \
    libelf-dev \
    bison \
    flex \
    libedit-dev \
    clang-format \
    python3-pyroute2 \
    luajit \
    libluajit-5.1-dev \
    arping \
    iperf \
    ethtool \
    devscripts \
    zlib1g-dev \
    libfl-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install specific version of pip
RUN python3.8 -m pip install --upgrade pip

# Install dependencies for libbcc
ENV BCC_VERSION v0.20.0
RUN git clone --depth 1 --branch "$BCC_VERSION" https://github.com/iovisor/bcc.git /usr/src/bcc \
	&& ( \
		cd /usr/src/bcc \
		&& mkdir build \
		&& cd build \
		&& cmake .. -DCMAKE_INSTALL_PREFIX=/usr \
		&& make \
		&& make install \
	) \
	&& rm -rf /usr/src/bcc

# Set work directory
RUN mkdir /work
WORKDIR /work

# Clone FlameGraph repository
RUN git clone --depth 1 https://github.com/brendangregg/FlameGraph

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports
EXPOSE 5005
EXPOSE 5006
EXPOSE 5007
EXPOSE 5000

# Run application
CMD ["python3", "udp.py"]
