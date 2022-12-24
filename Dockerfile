FROM python:3.11.1

ENV \
  # python:
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  # poetry:
  POETRY_VERSION=1.3.1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_HOME='/usr/local'

RUN \
  apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y \
    curl \
    postgresql-client \
  # installing poetry:
  && curl -sSL "https://install.python-poetry.org" | python - \
  && poetry --version

WORKDIR /bot

COPY pyproject.toml poetry.lock /bot/

RUN \
  poetry version \
  # install dependencies:
  && poetry run pip install -U pip \
  && poetry install --only main --no-interaction --no-ansi

COPY . /bot/
