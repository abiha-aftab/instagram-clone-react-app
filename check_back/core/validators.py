from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif']
VIDEO_EXTENSIONS = ['mp4', 'webm', 'mov']

MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_VIDEO_BYTES = 25 * 1024 * 1024


@deconstructible
class MaxFileSizeValidator:
    def __init__(self, max_bytes):
        self.max_bytes = max_bytes

    def __call__(self, file):
        if file.size > self.max_bytes:
            limit_mb = self.max_bytes // (1024 * 1024)
            raise ValidationError(f'File too large: the limit is {limit_mb} MB.', code='file_too_large')

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and other.max_bytes == self.max_bytes


image_extension_validator = FileExtensionValidator(IMAGE_EXTENSIONS)
image_size_validator = MaxFileSizeValidator(MAX_IMAGE_BYTES)


def validate_story_media(file):
    """Stories accept an image or a short video, each with its own size cap."""
    extension = Path(file.name).suffix.lower().lstrip('.')
    if extension in IMAGE_EXTENSIONS:
        MaxFileSizeValidator(MAX_IMAGE_BYTES)(file)
    elif extension in VIDEO_EXTENSIONS:
        MaxFileSizeValidator(MAX_VIDEO_BYTES)(file)
    else:
        allowed = ', '.join(IMAGE_EXTENSIONS + VIDEO_EXTENSIONS)
        raise ValidationError(f'Unsupported file type. Allowed: {allowed}.', code='invalid_extension')
