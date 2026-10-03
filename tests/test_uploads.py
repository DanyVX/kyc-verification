from io import BytesIO

import pytest
from PIL import Image

from kyc.api.uploads import UploadRejected, validate_image_upload


def png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (20, 20), "white").save(buffer, format="PNG")
    return buffer.getvalue()


def test_magic_bytes_and_image_decode_are_checked() -> None:
    validate_image_upload(png_bytes())
    with pytest.raises(UploadRejected):
        validate_image_upload(b"not an image")
