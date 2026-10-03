# Design

## Decisions

### 2026-10-03 — synthetic-first, adapter-based pipeline

Options: integrate heavy OCR/biometric models immediately, or keep them behind interfaces while delivering a reproducible core. Chosen: adapter boundaries with deterministic mocks. This makes the workflow testable on CPU while keeping replacement points for PaddleOCR, Tesseract, and approved face/liveness packages. It deliberately does not make performance claims.

### 2026-10-03 — decision rules in YAML

Rules are versioned configuration rather than scattered conditionals. Stored decisions include the rule-set version, so a policy update never rewrites historical evidence.

### 2026-10-03 — CNIC gender convention excluded

The often-repeated final-digit gender convention has not been verified from a suitable authoritative source here. It is **not** a hard validation rule. The system checks only documented format and date consistency.

## Synthetic template

The card has a cream background, clear `SAMPLE — NOT A REAL ID` watermark, and English fields: name, father/husband, gender, CNIC, DOB, issue, expiry. It is intentionally unlike an official document and includes no official logo, seal, hologram, or branding.
