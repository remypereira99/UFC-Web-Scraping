FROM python:3.12-slim-bookworm
WORKDIR /usr/local/app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY src/ ./src/
