# Security Policy

## No Secrets

Do not commit secrets to this repository. This includes API keys, broker
credentials, access tokens, passwords, private keys, account identifiers, or
any other sensitive authentication material.

## Environment Files

`.env` files must never be committed. Use `.env.example` only for safe,
non-sensitive placeholder configuration names and documentation.
.env files must never be committed.

## Data Policy

Do not commit real market datasets, broker exports, provider API responses,
private validation artifacts, account files, logs, database files, or generated
analysis artifacts. Local data folders are intentionally ignored except for
placeholder `.gitkeep` files.

## API Key Policy

API keys must be supplied only through local environment variables or another
approved secret-management mechanism outside the repository. Keys must not be
printed, logged, stored in fixtures, written to documentation, or captured in
test snapshots.
Keys must not be printed, logged, stored in fixtures.

## Responsible Disclosure

To report a security issue, contact: `security-contact@example.com`.

Please include a concise description, affected files or components, and safe
reproduction steps. Do not include live credentials or private datasets in the
report.
