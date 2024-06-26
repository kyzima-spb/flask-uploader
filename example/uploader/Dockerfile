FROM kyzimaspb/flask:3.11-slim-bookworm

LABEL maintainer="Kirill Vercetti <office@kyzima-spb.com>"

ARG DOWNLOAD_URL="https://github.com/kyzima-spb/flask-uploader/archive/refs/heads/dev-master.zip"

RUN pip install \
        --no-cache-dir \
        --disable-pip-version-check \
            "flask-uploader[aws] @ ${DOWNLOAD_URL}" \
            "flask-uploader[pymongo] @ ${DOWNLOAD_URL}" \
    && mkdir /upload && chown user:user /upload && chmod 1777 /upload

VOLUME /upload

COPY ./requirements.txt ./

RUN pip install \
        --no-cache-dir \
        --disable-pip-version-check \
        -r requirements.txt

COPY . ./
