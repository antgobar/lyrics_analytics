FROM python:3.10.2-slim-buster
WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/lyrics_analytics"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . .
RUN pip install poetry==1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev