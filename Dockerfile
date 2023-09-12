FROM python:3.11-slim

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN : \
    && apt-get -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN : \
    && pip install --no-cache -r requirements.txt

ENTRYPOINT ["gunicorn", "app.main:app", "--worker-class", "uvicorn.workers.UvicornH11Worker"]
