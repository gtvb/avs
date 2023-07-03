# syntax=docker/dockerfile:1.3

FROM python:3.10 as build-stage

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=100

RUN python -m venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY ["requirements.txt", "/app/"]

RUN pip install -r requirements.txt

FROM python:3.10-slim-bookworm as final

RUN apt-get -y update
RUN apt-get install ffmpeg espeak-ng -y

RUN useradd -m avs_user
USER avs_user

ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app

COPY --from=build-stage --chown=avs_user $VIRTUAL_ENV $VIRTUAL_ENV
COPY --chown=avs_user [".", "/app"]
