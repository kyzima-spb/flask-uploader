FROM kyzimaspb/flask:3.10-slim-bullseye

LABEL maintainer="Kirill Vercetti <office@kyzima-spb.com>"

COPY ./requirements.txt /app/requirements.txt

RUN pydep.sh

RUN pip install -q \
        --no-cache-dir \
        --disable-pip-version-check \
        --extra-index-url=https://test.pypi.org/simple \
        --extra-index-url=https://pypi.python.org/simple \
        flask-uploader[dev]

ADD ./ /app
