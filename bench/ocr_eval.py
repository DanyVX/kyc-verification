"""Run OCR evaluation only after an engine is installed; writes measured JSON, never estimates."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from kyc.ocr.engines import require_engine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--engine", choices=["paddleocr", "tesseract"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    engine = require_engine(args.engine)
    rows: list[dict[str, object]] = []
    for image_path in sorted(args.dataset.glob("*.png")):
        truth = json.loads(image_path.with_suffix(".json").read_text(encoding="utf-8"))
        outcome = engine.extract(image_path.read_bytes())
        text = outcome.fields.get("raw_text", "")
        rows.append(
            {
                "sample": image_path.name,
                "engine": outcome.engine,
                "confidence": outcome.confidence,
                "cnic_exact_match": truth["cnic"] in text,
            }
        )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "commit": commit,
                "platform": platform.platform(),
                "engine": args.engine,
                "samples": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
