import json


SECRET_KEY = 'Very secret string'

UPLOADER_ROOT_DIR = 'upload'
UPLOADER_INSTANCE_RELATIVE_ROOT = True

MONGO_URI = 'mongodb://user:demo@mongo/uploader?authSource=admin'

with open('/run/secrets/aws_credentials') as f:
    aws_credentials = json.load(f)
    AWS_ACCESS_KEY_ID = aws_credentials['aws_access_key']
    AWS_SECRET_ACCESS_KEY = aws_credentials['aws_secret_access_key']

AWS_REGION_NAME = 'ru-central1'
AWS_ENDPOINT_URL = 'https://storage.yandexcloud.net'
