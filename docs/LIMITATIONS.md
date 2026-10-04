# Limitations

- Synthetic success does not transfer to real IDs, real faces, or production fraud. The bundled
  “selfies” are geometric avatars, so neither face matching nor liveness can be evaluated from them.
- No government database verification, checksum claim, or identity proof is provided.
- Default face and liveness adapters are mocks; they never substantiate biometric accuracy.
- Urdu OCR is best-effort only and is not measured in this release.
- Fairness across skin tone, lighting, age, disability, and cameras cannot be measured on this synthetic dataset.
- Watermark-removal attacks and adversarial/deepfake resistance are out of scope.
