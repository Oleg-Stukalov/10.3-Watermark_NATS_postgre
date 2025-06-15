# bot/database/migration/Dockerfile

FROM ghcr.io/withlogicco/poetry:1.7.1-python-3.12

WORKDIR /app

# Copy only the files needed to install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# Copy the whole project (including bot/, config.py, etc.)
COPY . .

# Default: run Alembic migration
CMD ["poetry", "run", "alembic", "upgrade", "head"]
