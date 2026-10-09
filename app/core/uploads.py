import warnings

from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError

MAX_IMAGE_PIXELS = 20_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_image_file(source, max_bytes):
    if source and getattr(source, "size", 0) > max_bytes:
        raise ValidationError(f"La imagen no puede superar los {max_bytes // (1024 * 1024)} MB.")
    if not source:
        return source
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(source)
            image_format, width, height = image.format, image.width, image.height
            image.verify()
        if image_format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError("Usa una imagen JPEG, PNG o WebP.")
        if width * height > MAX_IMAGE_PIXELS:
            raise ValidationError("La imagen tiene demasiados píxeles. Usa una versión más pequeña.")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValidationError("La imagen no es válida o está dañada.")
    finally:
        source.seek(0)
    return source
