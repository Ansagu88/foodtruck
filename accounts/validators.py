"""
This module contains custom validators for the accounts app.
"""

import os
from django.core.exceptions import ValidationError


def allow_only_images_validator(value):
    """
    Validates if the given file has a valid image extension.

    Args:
        value (File): The file to be validated.

    Raises:
        ValidationError: If the file extension is not supported.

    Returns:
        None
    """
    ext = os.path.splitext(value.name)[1]  # cover-image.jpg
    print(ext)
    valid_extensions = [".png", ".jpg", ".jpeg"]
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            "Unsupported file extension. Allowed extensions: " + str(valid_extensions)
        )
