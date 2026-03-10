FROM ubuntu:22.04

# Configure timezone to avoid interactive prompt during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# Replace default sources with Aliyun mirrors and install Python
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y python3 python3-pip tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install required Python packages using Aliyun PyPI mirror
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ dnslib flask

# Copy the Python script into the container
COPY dnslog.py /app/dnslog.py

# Expose ports: 53 (UDP) for DNS, 80 (TCP) for HTTP
EXPOSE 53/udp 80/tcp

# Run the Python server
CMD ["python3", "dnslog.py"]