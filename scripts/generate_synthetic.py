"""Generate the reproducible synthetic demo corpus; it never downloads or uses personal data."""

from __future__ import annotations

import argparse
from pathlib import Path

from kyc.synth.generator import generate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--out", type=Path, default=Path("data/synthetic"))
    args = parser.parse_args()
    generate(args.seed, args.out, args.count)
    print(
        f"Generated {args.count} synthetic cards and paired geometric-avatar selfies in {args.out}"
    )


if __name__ == "__main__":
    main()
