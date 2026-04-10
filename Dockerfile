# Stage 1: Build stage
FROM python:3.11-bookworm AS builder

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-bookworm

# The app talks to the host Docker daemon via the mounted socket,
# so the Docker CLI package is enough here.
RUN apt-get update && \
    apt-get install --no-install-recommends -y bash docker.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

WORKDIR /code

COPY . /code/
