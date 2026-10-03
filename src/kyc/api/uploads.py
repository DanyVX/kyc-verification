from __future__ import annotations

from PIL import Image


class UploadRejected(ValueError):
    pass


IMAGE_MAGIC = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")


def validate_image_upload(payload: bytes, max_bytes: int = 8 * 1024 * 1024) -> None:
    if len(payload) > max_bytes:
        raise UploadRejected("upload too large")
    if not payload.startswith(IMAGE_MAGIC):
        raise UploadRejected("unsupported image type")
    try:
        with Image.open(__import__("io").BytesIO(payload)) as image:
            image.verify()
            if image.width * image.height > 30_000_000:
                raise UploadRejected("image dimensions too large")
    except UploadRejected:
        raise
    except Exception as exc:
        raise UploadRejected("invalid image") from exc
