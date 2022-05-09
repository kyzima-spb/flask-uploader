from setuptools import setup


setup(
    install_requires=[
        'flask>=2',
    ],
    extras_require={
        'pymongo': [
            'flask-pymongo>=2.3',
        ],
    },
)