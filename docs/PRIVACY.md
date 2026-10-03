# Privacy and retention

The API is designed for synthetic demo inputs only. Raw artifacts and extracted fields are encrypted before persistence; plaintext CNIC values are not written to audit logs. Raw artifacts default to a 24-hour retention window. A purge routine and erase endpoint remove session artifacts. Admin views should mask identifiers to the final four digits. Clients must capture consent before any non-synthetic deployment; no such deployment is supported by this demo.
