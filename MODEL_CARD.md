# Model card

No trained model ships in v0.1.0. OCR, face match, and liveness are adapter boundaries. The default adapters are deterministic mocks so the test suite is reproducible and does not imply real biometric performance.

The optional `face-recognition-pipeline` companion repository documents its InsightFace model pack as non-commercial research-only. This project does not vendor it, does not claim commercial suitability, and must not enable that adapter without independently confirming the model terms. The optional `liveness-detection` HTTP adapter consumes its documented `/v1/decide` response contract, but no liveness model or metric is included here.
