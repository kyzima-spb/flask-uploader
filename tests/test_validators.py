from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage
from PIL import Image

from flask_uploader.validators import (
    ImageSize,
    ValidationError,
)


def test_unsupported_image():
    storage = FileStorage(BytesIO(b'Text file'), 'input.txt')
    validator = ImageSize(min_width=100)
    with pytest.raises(ValidationError):
        validator(storage)


@pytest.mark.parametrize('params', (
    {},
    {'min_width': -1},
    {'min_height': -2},
    {'max_width': -3},
    {'max_height': -4},
    {'min_width': -1, 'min_height': -2, 'max_width': -3, 'max_height': -4},
))
def test_required_one_size_option(params):
    with pytest.raises(ValueError, match=r'At least one of the size options must be given\.'):
        ImageSize(**params)


@pytest.mark.parametrize('params', (
    {'min_width': 10, 'max_width': 1},
))
def test_invalid_width_range(params):
    with pytest.raises(ValueError, match=r'The minimum width must be less than the maximum\.'):
        ImageSize(**params)


@pytest.mark.parametrize('params', (
    {'min_height': 10, 'max_height': 1},
))
def test_invalid_height_range(params):
    with pytest.raises(ValueError, match=r'The minimum height must be less than the maximum\.'):
        ImageSize(**params)


@pytest.mark.parametrize('params,size', (
    ({'min_width': 200, 'min_height': 200, 'max_width': 200, 'max_height': 200}, (100, 100)),
    ({'min_width': 200, 'max_width': 200}, (100, 200)),
    ({'min_height': 200, 'max_height': 200}, (200, 100)),
    ({'min_width': 200, 'min_height': 200}, (100, 100)),
    ({'max_width': 100, 'max_height': 100}, (200, 200)),
    ({'min_width': 200}, (100, 200)),
    ({'max_width': 100}, (200, 100)),
    ({'min_height': 200}, (200, 100)),
    ({'max_height': 100}, (100, 200)),
))
def test_validate_image(params, size):
    validator = ImageSize(**params)
    img = Image.new('RGB', size)
    with pytest.raises(ValidationError, match=r'Invalid image size\.'):
        validator.validate_image(img)


def test_custom_message(mocker):
    mock_img = mocker.Mock(size=(100, 100))
    validator = ImageSize(
        min_width=200,
        min_height=200,
        message='Image size %(width)dx%(height)dpx less then %(min_width)dx%(min_height)dpx.',
    )
    with pytest.raises(ValidationError, match=r'Image size 100x100px less then 200x200px\.'):
        validator.validate_image(mock_img)
