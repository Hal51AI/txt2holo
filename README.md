txt2holo
========
[![mypy](https://github.com/jjangsangy/txt2holo/actions/workflows/mypy.yml/badge.svg)](https://github.com/jjangsangy/txt2holo/actions/workflows/mypy.yml)

Convert text prompts into a 2d holographic images

# Setup
Install dependencies with pip

```bash
pip install -r requirements.txt
```

# Run
First make sure to fill out the environment variables in the `.env.example` file and rename it to `.env`

Run application by pointing `uvicorn` to the python module
```bash
uvicorn app.main:app
```

# Docker
Run this in a containerized environment with docker

```bash
docker build -it txt2holo .
```

Then run with

```bash
docker run -it -p 8000:8000 -e STABILITY_API_KEY=<API_KEY> txt2holo
```

## Docker Compose
An easier way to run a container is to fill out the `docker-compose-example.yml`, rename it to `docker-compose.yml` and run

```bash
docker compose up
```