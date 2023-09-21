ARG RUNNING_ENV=prod
FROM python:3.9.11-alpine3.15 AS base

WORKDIR /app
COPY ./requirements* /app/
RUN apk --no-cache add --virtual build-dependencies \
            build-base \
            libc-dev \
            libffi-dev \
            linux-headers \
            mariadb-dev \
      && apk --no-cache add \
            curl \
            bash \
            gcc \
            mariadb-connector-c-dev \
            git \
            openssh-client \
      && pip install -U pip --no-cache-dir \
      && pip install -r requirements.txt

FROM base AS base_prod
COPY . /app/
CMD python entrypoint.py

FROM base AS base_local

FROM base_${RUNNING_ENV} AS final_stage
RUN apk del build-dependencies
