FROM kyzimaspb/docker-sphinx

RUN pip install -q \
        --no-cache-dir \
        --disable-pip-version-check \
        --extra-index-url=https://test.pypi.org/simple \
        --extra-index-url=https://pypi.python.org/simple \
            flask-uploader \
            flask-uploader[pymongo] \
            flask-uploader[aws]

ADD ./ /docs/source/
