"""Run the fully offline synthetic demo; all model-like signals are explicitly simulated."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from kyc.decision import DecisionEngine
from kyc.domain import SignalBundle
from kyc.synth.generator import generate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--data-dir", type=Path, default=Path("data/synthetic-demo"))
    parser.add_argument("--result", type=Path, default=Path("results/synthetic-demo.json"))
    args = parser.parse_args()
    generate(args.seed, args.data_dir, args.count)
    engine = DecisionEngine(Path("config/decision-rules.yaml"))
    # These values model a known-good synthetic fixture, not real OCR/biometric outputs.
    decision = engine.decide(SignalBundle(ocr_confidence=1.0, face_similarity=1.0, liveness="LIVE"))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "commit": commit,
        "platform": platform.platform(),
        "seed": args.seed,
        "cards": args.count,
        "signal_source": "simulated known-good synthetic fixture; not OCR/face/liveness inference",
        "decision": decision.model_dump(mode="json"),
    }
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
