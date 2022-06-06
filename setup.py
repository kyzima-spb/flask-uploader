from setuptools import setup


aws_requires = [
    'boto3>=1.22',
]
pymongo_requires = [
    'flask-pymongo>=2.3',
]


setup(
    install_requires=[
        'flask>=2',
        'Flask-WTF>=1.0',
        'Pillow>=9.1.1',
    ],
    extras_require={
        'aws': aws_requires,
        'dev': [
            'pytest>=7.1',
            'pytest-mock>=3.7',
            'boto3-stubs-lite[s3]',
            'mypy>=0.950',
            'types-pillow',
            *aws_requires,
            *pymongo_requires,
        ],
        'pymongo': pymongo_requires,
    },
)
