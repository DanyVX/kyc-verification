from io import BytesIO

from PIL import Image

from kyc.doc.normalize import normalize_orientation


def test_normalization_returns_png() -> None:
    source = BytesIO()
    Image.new("RGB", (20, 10), "white").save(source, format="JPEG")
    normalized = normalize_orientation(source.getvalue())
    assert normalized.startswith(b"\x89PNG\r\n\x1a\n")
