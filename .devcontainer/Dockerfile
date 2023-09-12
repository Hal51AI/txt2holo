FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN : \
    && apt-get -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*