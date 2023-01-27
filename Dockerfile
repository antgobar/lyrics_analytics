FROM python:3.10.2-slim-buster as build
WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/lyrics_analytics"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY lyrics_analytics /usr/src/app/lyrics_analytics
COPY pyproject.toml poetry.lock .env.secrets README.md /usr/src/app/
RUN pip install poetry==1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
FROM build as run
COPY --from=build /usr/src/app/lyrics_analytics/ /usr/src/app/lyrics_analytics/
ENTRYPOINT ["flask", "--app", "lyrics_analytics.api", "--debug", "run", "-h", "0.0.0.0"]