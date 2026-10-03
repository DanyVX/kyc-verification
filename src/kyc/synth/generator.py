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


def generate(seed: int, output_dir: Path, count: int = 500) -> None:
    """Create visibly fictional cards and sidecar ground truth. No faces or real IDs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    fake = Faker("en_US")
    fake.seed_instance(seed)
    font = ImageFont.load_default()
    for index in range(count):
        gender = rng.choice(["M", "F"])
        identity = SyntheticIdentity(fake.name(), fake.name(), gender, f"{rng.randrange(10000,99999)}-{rng.randrange(1000000,9999999)}-{rng.randrange(10)}", fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"), "01.01.2020", "01.01.2030")
        card = Image.new("RGB", (900, 560), "#e8e2cc")
        draw = ImageDraw.Draw(card)
        draw.rectangle((10, 10, 890, 550), outline="#9b2c2c", width=8)
        draw.text((70, 45), "SAMPLE — NOT A REAL ID", fill="#9b2c2c", font=font, stroke_width=1)
        for row, (label, value) in enumerate(asdict(identity).items()):
            draw.text((80, 150 + row * 52), f"{label.upper()}: {value}", fill="#202020", font=font)
        path = output_dir / f"sample-{index:04d}.png"
        card.save(path)
        path.with_suffix(".json").write_text(json.dumps(asdict(identity), indent=2), encoding="utf-8")
