FROM python:3.12-slim-bookworm
WORKDIR /usr/local/app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

ENTRYPOINT ["/bin/sh", "-c"]
