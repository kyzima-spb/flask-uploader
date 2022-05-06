FROM kyzimaspb/docker-sphinx

RUN pip install -q \
        --no-cache-dir \
        --disable-pip-version-check \
        --extra-index-url=https://test.pypi.org/simple \
            flask-uploader

ADD ./ /docs/source/
