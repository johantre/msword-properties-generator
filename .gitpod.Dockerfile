FROM python:slim

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    openjdk-17-jdk \
    curl \
    unzip \
    git \
    docker \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspace

# Default command
CMD [ "bash" ]