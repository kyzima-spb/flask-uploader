FROM kyzimaspb/flask:3.11-slim-bookworm

LABEL maintainer="Kirill Vercetti <office@kyzima-spb.com>"

ARG DOWNLOAD_URL="https://github.com/kyzima-spb/flask-uploader/archive/refs/heads/dev-master.zip"

RUN set -ex \
    && pip install \
        --no-cache-dir \
        --disable-pip-version-check \
            "flask-uploader[aws] @ ${DOWNLOAD_URL}" \
            "flask-uploader[pymongo] @ ${DOWNLOAD_URL}"

COPY ./requirements.txt ./

RUN set -ex \
    && pip install \
        --no-cache-dir \
        --disable-pip-version-check \
        -r requirements.txt

COPY . ./
