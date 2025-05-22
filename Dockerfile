FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ADD pyproject.toml uv.lock /app

RUN uv sync --locked --no-dev

ADD src/ /app

CMD ["uv", "run", "--no-dev", "main.py", "--redis-host", "redis", "--redis-port", "6379", "--redis-db", "0"]
