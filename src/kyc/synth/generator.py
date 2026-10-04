from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from faker import Faker
from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class SyntheticIdentity:
    name: str
    father_name: str
    gender: str
    cnic: str
    dob: str
    issue: str
    expiry: str


def _synthetic_selfie(seed: int, label: str) -> Image.Image:
    """A non-human geometric avatar—not a biometric image or a face-recognition claim."""
    rng = random.Random(seed)
    image = Image.new("RGB", (320, 320), (230, 235, 240))
    draw = ImageDraw.Draw(image)
    color = tuple(rng.randrange(40, 210) for _ in range(3))
    draw.ellipse((70, 45, 250, 225), fill=color, outline="#202020", width=4)
    draw.rectangle((70, 225, 250, 315), fill=color)
    draw.text((8, 8), f"SYNTHETIC AVATAR — {label}", fill="#9b2c2c", font=ImageFont.load_default())
    return image


def generate(seed: int, output_dir: Path, count: int = 500) -> None:
    """Create visibly fictional cards and sidecar ground truth. No faces or real IDs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    fake = Faker("en_US")
    fake.seed_instance(seed)
    font = ImageFont.load_default()
    for index in range(count):
        gender = rng.choice(["M", "F"])
        identity = SyntheticIdentity(
            fake.name(),
            fake.name(),
            gender,
            f"{rng.randrange(10000, 99999)}-{rng.randrange(1000000, 9999999)}-{rng.randrange(10)}",
            fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"),
            "01.01.2020",
            "01.01.2030",
        )
        card = Image.new("RGB", (900, 560), "#e8e2cc")
        draw = ImageDraw.Draw(card)
        draw.rectangle((10, 10, 890, 550), outline="#9b2c2c", width=8)
        draw.text((70, 45), "SAMPLE — NOT A REAL ID", fill="#9b2c2c", font=font, stroke_width=1)
        for row, (label, value) in enumerate(asdict(identity).items()):
            draw.text((80, 150 + row * 52), f"{label.upper()}: {value}", fill="#202020", font=font)
        path = output_dir / f"sample-{index:04d}.png"
        card.save(path)
        match = output_dir / f"sample-{index:04d}-selfie-match.png"
        mismatch = output_dir / f"sample-{index:04d}-selfie-mismatch.png"
        _synthetic_selfie(seed + index, "MATCH").save(match)
        _synthetic_selfie(seed + count + index, "MISMATCH").save(mismatch)
        truth = {
            **asdict(identity),
            "id_image": path.name,
            "matching_selfie": match.name,
            "mismatching_selfie": mismatch.name,
            "category": "genuine",
            "biometric_note": "geometric avatar only; not a human face",
        }
        path.with_suffix(".json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
