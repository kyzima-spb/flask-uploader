FROM python:3.7-slim-bookworm

ENV HOME /tmp
ENV PYTHONPATH /flask-uploader/src

WORKDIR /flask-uploader

COPY ./pyproject.toml .

RUN set -ex \
    && pip install \
        --no-cache-dir \
        --disable-pip-version-check \
          -e . \
          -e .[aws] \
          -e .[pymongo] \
          -e .[dev]
