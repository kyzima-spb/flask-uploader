from setuptools import setup


setup(
    install_requires=[
        'flask>=2',
        'Pillow>=9.1',
    ],
    extras_require={
        'aws': [
            'boto3>=1.22',
        ],
        'pymongo': [
            'flask-pymongo>=2.3',
        ],
    },
)