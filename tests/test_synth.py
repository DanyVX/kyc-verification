import json
from pathlib import Path

from kyc.synth.generator import generate


def test_generator_is_reproducible_and_watermarked(tmp_path: Path) -> None:
    generate(7, tmp_path, count=2)
    assert len(list(tmp_path.glob("sample-????.png"))) == 2
    assert len(list(tmp_path.glob("*.png"))) == 6
    payload = json.loads((tmp_path / "sample-0000.json").read_text())
    assert len(payload["cnic"].replace("-", "")) == 13
    assert (tmp_path / payload["matching_selfie"]).exists()
    assert (tmp_path / payload["mismatching_selfie"]).exists()
