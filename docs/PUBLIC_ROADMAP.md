# MarketMind AI Public Roadmap

This document is the public-safe status and roadmap for the
`marketmind-ai-foundation` release. It intentionally excludes private project
memory, proprietary calibration plans, real datasets, API responses, and private
validation artifacts.

## Current Phase

MarketMind AI is in Phase 2: Data & Validation.

The current public release is an engine-first foundation for a Smart Money
Intelligence Platform. The codebase focuses on deterministic contracts,
in-memory utilities, data quality governance, and validation boundaries before
any user-facing workflow or external data dependency is introduced.

## Implemented Public-Safe Components

- Daily market data contracts and fail-fast dataset validation.
- Feature contracts and deterministic feature utilities.
- Deterministic signal foundations for accumulation, distribution, absorption,
  fake-move detection, and liquidity utility values.
- Smart Money score contract and fixed V1 score computation over validated
  signal objects.
- Market phase contracts, explicit parameter contracts, and deterministic phase
  computation.
- Confidence contracts and deterministic confidence computation.
- Validation result contracts and in-memory validation utility foundations.
- Data source metadata contracts, metadata evaluation, and eligibility gating.
- Local CSV ingestion contracts, local CSV ingestion utility, quality validation
  orchestration, and batch-run result contracts.
- Data Quality Gate behavior over existing quality result records.
- Managed API provider boundary contracts, credential-access result contracts,
  credential-presence reader, runtime credential-use boundary, fetch request and
  result contracts, adapter port contracts, and preflight guards.
- Tiingo planning metadata and fixture-oriented parsing/adapter boundaries used
  by tests without approving real provider access.
- Smoke tests covering contracts, boundaries, governance, and deterministic
  utility behavior.

## Limitations

- No trading advice is provided.
- No AI model is currently implemented.
- No real data conclusions are produced.
- No real market dataset is included.
- No provider API response data is included.
- No external provider access is approved by this public release.
- No live broker or exchange integration is included.
- No persistence layer or database-backed workflow is implemented.
- No UI is implemented.
- No proprietary calibration, advanced Smart Money Engine v2 logic, or private
  validation artifacts are included.

## Data and Provider Boundaries

Local CSV support is currently a validation foundation only. Public placeholder
folders are kept for `data/raw`, `data/processed`, and `artifacts`, but real
datasets, generated reports, API responses, databases, logs, and private
validation outputs are excluded. In short, private validation outputs are
excluded. Private validation outputs are excluded.
private validation outputs are excluded.

Managed API code is boundary-oriented. The public foundation includes provider
metadata contracts, credential-access result contracts, a credential-presence
reader, a runtime credential-use boundary, fetch request/result contracts,
adapter port contracts, preflight guards, and Tiingo planning/test boundaries.
These components do not approve a provider, verify provider access, verify
credential correctness, ingest API data, persist data, run engine logic, approve
source reliability, approve live use, or produce market conclusions. They do
not approve a provider, they do not verify provider access, they do not verify
credential correctness, they do not ingest API data, they do not persist data,
they do not run engine logic, and they do not produce market conclusions.
These components do not verify credential correctness.
These components do not approve source reliability.
These components do not approve live use.
No source is approved for historical reliability.

Tiingo planning/test boundaries are included only as planning and test
boundaries. Tiingo references in the public foundation are planning and test
boundaries only. Tests use fixture payloads, fake transports, or injected
callables. No real Tiingo response payload is included. No real Tiingo response
payload, API key, account output, or provider validation artifact is included.
No provider API response data is included.
Tiingo references in the public foundation are planning and test boundaries.
Tiingo planning/test boundaries are planning and test boundaries only.
Tests use fixture payloads, fake transports, and injected callables.
No real provider API response is included.

Credential handling must remain secret-safe. Runtime code must not read `.env`
files, print raw credentials, store raw credentials, write raw credentials to
fixtures, or place raw credentials in public documentation. Runtime code must
not read `.env`, must not print raw credentials, must not store raw credentials,
must not write raw credentials to fixtures, and must not place raw credentials
in public documentation.

## Future Roadmap

Planned public-safe directions include:

- Strengthen daily data quality checks and evidence records.
- Expand local CSV validation examples using synthetic or public-safe fixtures.
- Maintain the public-safe multi-asset data acquisition strategy in
  `docs/MULTI_ASSET_DATA_ACQUISITION_STRATEGY.md` as governance only.
- Add clearer reporting around dataset eligibility and quality gate outcomes.
- Add an AI-ready explainability roadmap that explains verified engine outputs
  without creating unsupported conclusions.
- Add public documentation for architecture, testing discipline, and security
  boundaries.

Private or future-gated directions include:

- Advanced Smart Money Engine v2 research.
- Proprietary calibration and parameter research.
- Real provider access verification.
- Real dataset validation and provider cross-check workflows.
- Private evidence artifacts and strategy validation materials.

## Public Release Boundary

This repository is intended to show architecture, governance, deterministic
engine foundations, and testing discipline. It should not be treated as an
investment system, a broker integration, an execution system, or a source of
market conclusions.
