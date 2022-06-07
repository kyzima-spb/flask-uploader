Flask-Uploader
==============

|PyPI| |LICENCE| |STARS| |DOCS|

**Flask-Uploader** - file uploader for Flask with flexible extensibility.

How to use can be found in the documentation_.
Documentation is in Russian only, use a translator for other languages.

See the usage example_ for more understanding.

Development
-----------

Run mypy::

    docker-compose exec -w /package -u 1000:1000 sphinx mypy

Run pytest::

    docker-compose exec -w /package -u 1000:1000 sphinx pytest

.. |PyPI| image:: https://img.shields.io/pypi/v/flask-uploader.svg
   :target: https://pypi.org/project/flask-uploader/
   :alt: Latest Version

.. |LICENCE| image:: https://img.shields.io/github/license/kyzima-spb/flask-uploader.svg
   :target: https://github.com/kyzima-spb/flask-uploader/blob/master/LICENSE
   :alt: MIT

.. |STARS| image:: https://img.shields.io/github/stars/kyzima-spb/flask-uploader.svg
   :target: https://github.com/kyzima-spb/flask-uploader/stargazers
   :alt: GitHub stars

.. |DOCS| image:: https://readthedocs.org/projects/flask-uploader/badge/?version=latest
   :target: https://flask-uploader.readthedocs.io/ru/latest/?badge=latest
   :alt: Documentation Status

.. _documentation: https://flask-uploader.readthedocs.io/ru/latest/
.. _example: https://github.com/kyzima-spb/flask-uploader/tree/master/example/uploader
