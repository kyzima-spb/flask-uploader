from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage
from PIL import Image

from flask_uploader.validators import (
    ImageSizeValidator,
    ValidationError,
)


def test_unsupported_image():
    storage = FileStorage(BytesIO(b'Text file'), 'input.txt')
    validator = ImageSizeValidator()
    with pytest.raises(ValidationError):
        validator(storage)


@pytest.mark.parametrize('params,error_msg', (
    ({'min_width': 10, 'max_width': 1}, 'The minimum width must be less than the maximum.'),
    ({'min_height': 10, 'max_height': 1}, 'The minimum height must be less than the maximum.'),
))
def test_validator_params(params, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        ImageSizeValidator(**params)


@pytest.mark.parametrize('params,size,error_msg', (
    (
        {'min_width': 200},
        (100, 200),
        r'The width of the image must be greater than or equal to \d+px\.',
    ),
    (
        {'max_width': 100},
        (200, 100),
        r'The image width must be less than or equal to \d+px\.',
    ),
    (
        {'min_height': 200},
        (200, 100),
        r'The height of the image must be greater than or equal to \d+px\.',
    ),
    (
        {'max_height': 100},
        (100, 200),
        r'The image height must be less than or equal to \d+px\.',
    ),
))
def test_validate_image(params, size, error_msg):
    validator = ImageSizeValidator(**params)
    img = Image.new('RGB', size)
    with pytest.raises(ValidationError, match=error_msg):
        validator.validate_image(img)
