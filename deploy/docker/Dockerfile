FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv git curl sqlite3 tree \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /openroot
COPY . /openroot/
RUN python3 -m venv venv && venv/bin/pip install --upgrade pip \
    && venv/bin/pip install numpy pandas
ENV PATH="/openroot/venv/bin:$PATH"
CMD ["/bin/bash", "-c", "echo 'OpenRoot Superlinear Spine Active' && exec bash"]
