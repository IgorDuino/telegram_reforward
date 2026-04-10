# Stage 1: Build stage
FROM python:3.11-bookworm AS builder

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-bookworm

# The app talks to the host Docker daemon via the mounted socket.
# It also calls `docker compose`, so the Compose CLI plugin must exist
# inside the container.
RUN apt-get update && \
    apt-get install --no-install-recommends -y bash ca-certificates curl && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install --no-install-recommends -y docker-ce-cli docker-compose-plugin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

WORKDIR /code

COPY . /code/
