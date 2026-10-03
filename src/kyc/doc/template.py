from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldRoi:
    name: str
    left: float
    top: float
    right: float
    bottom: float


# Fractional ROIs for the deliberately non-official synthetic template.
SYNTHETIC_FRONT_ROIS = (
    FieldRoi("name", 0.08, 0.26, 0.90, 0.34),
    FieldRoi("cnic", 0.08, 0.44, 0.90, 0.52),
    FieldRoi("dob", 0.08, 0.53, 0.90, 0.61),
)
