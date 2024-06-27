FROM kyzimaspb/flask:3.11-slim-bookworm

LABEL maintainer="Kirill Vercetti <office@kyzima-spb.com>"

ARG DOWNLOAD_URL="https://github.com/kyzima-spb/flask-uploader/archive/refs/heads/dev-master.zip"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --disable-pip-version-check \
        "flask-uploader[aws] @ ${DOWNLOAD_URL}" \
        "flask-uploader[pymongo] @ ${DOWNLOAD_URL}" \
    && mkdir /upload && chown user:user /upload && chmod 1777 /upload

VOLUME /upload

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=./requirements.txt,target=requirements.txt \
    pip install --disable-pip-version-check -r requirements.txt

COPY ./uploader ./uploader
