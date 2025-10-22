FROM python:3.12-slim-trixie

ENV PYTHONUNBUFFERED=1

WORKDIR /app
# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
COPY app /app/app
COPY tests /app/tests
COPY scripts /app/scripts
COPY uv.lock pyproject.toml alembic.ini /app/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0"]