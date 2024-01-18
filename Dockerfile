# Stage 1: Build stage
FROM python:3.11-buster AS builder

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-buster

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

WORKDIR /code

COPY . /code/
