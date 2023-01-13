FROM python:3.10.2-slim-buster
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY poetry.lock .
COPY pyproject.toml .
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - --version 1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
