FROM python:3.10.2-slim-buster as build
WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app/lyrics_analytics"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY lyrics_analytics /app/lyrics_analytics
COPY pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip
RUN pip install poetry==1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

FROM build as run

ARG FLASK_SECRET_KEY
ARG GENIUS_CLIENT_ACCESS_TOKEN
ARG MONGO_URI
ARG BROKER_URL
ARG RESULT_BACKEND

ENV FLASK_SECRET_KEY $FLASK_SECRET_KEY
ENV GENIUS_CLIENT_ACCESS_TOKEN $GENIUS_CLIENT_ACCESS_TOKEN
ENV MONGO_URI $MONGO_URI
ENV BROKER_URL $BROKER_URL
ENV RESULT_BACKEND $RESULT_BACKEND

COPY --from=build /app/lyrics_analytics/ /app/lyrics_analytics/