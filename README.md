# MarketMind AI

[![CI](https://github.com/ahmed369younis-hue/marketmind-ai-foundation/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmed369younis-hue/marketmind-ai-foundation/actions/workflows/ci.yml)

MarketMind AI is an **Engine-first Smart Money Intelligence Platform**
foundation. This public repository presents the deterministic core contracts,
data quality governance, validation boundaries, and early engine utilities that
support a future market-structure intelligence system.

The current release is named `marketmind-ai-foundation`. It is intentionally
limited to public-safe foundation code and documentation.

## Project Overview

MarketMind AI is designed around an engine-first workflow: define strict data
contracts, validate data quality, compute deterministic features and signal
foundations, and preserve clear evidence boundaries before adding UI, external
data access, persistence, or advanced intelligence layers.

The foundation emphasizes:

- data quality governance
- deterministic signal foundations
- explicit parameter contracts
- auditable validation boundaries
- AI-ready explainability roadmap

## Current Status

Current phase: Phase 2 - Data & Validation.

The repository contains Python contracts, pure in-memory utilities, local CSV
quality-validation foundations, managed API boundary contracts, and smoke tests.
No real datasets, provider responses, private validation artifacts, API keys, or
private project memory are included in the public release.

## What This Is

- A public-safe foundation for a Smart Money Intelligence Platform.
- A deterministic Python engine layer for market-structure research tooling.
- A contract-first codebase with strict validation and quality gates.
- A portfolio-quality architecture sample for data governance, signal
  foundations, and explainability planning.
- A base for future verified analysis workflows once data quality, source
  reliability, and evidence requirements are satisfied.

## What This Is Not

- Not an automated trading product.
- Not an entry or exit recommendation service.
- Not an advisory or portfolio-management product.
- Not a returns-guarantee system.
- Not a live execution or broker-control system.
- Not a forecasting system.
- Not a replacement for independent research, risk review, or professional
  judgment.

## Architecture

The codebase is organized by responsibility:

- `app/domain/` contains contracts, enums, parameter objects, and validation
  result shapes.
- `app/engine/` contains deterministic in-memory utilities for features,
  signals, scoring, phase classification, confidence, and validation checks.
- `app/data/` contains data-source metadata evaluation, local CSV validation,
  quality gates, managed API boundary utilities, and provider planning
  boundaries.
- `tests/smoke/` protects current behavior, project governance, and scope
  boundaries.
- `docs/PUBLIC_ROADMAP.md` describes the public-safe roadmap and current
  limitations.

Private project memory is intentionally excluded from the public release.

## Implemented Features

- Daily market data contract with fail-fast validation.
- Time-series utilities for rolling standard deviation, rolling slope, moving
  average, and period return.
- Feature utilities for range compression, volume trend, price momentum, volume
  spike, liquidity inflow, and liquidity outflow.
- Deterministic signal foundations for accumulation, distribution, absorption,
  fake-move detection, and signal aggregation.
- Smart Money score contract and fixed V1 score computation over validated
  signal records.
- Market phase contracts, explicit phase parameters, resolution policy, and
  deterministic phase computation.
- Confidence contracts and deterministic confidence computation.
- Validation result contracts and in-memory validation utility foundations.
- Data source metadata contracts, metadata-only evaluation, and eligibility
  gating.
- Local CSV ingestion contracts, ingestion utility, quality validation
  orchestration, and batch-run result contract.
- Managed API provider boundary contracts, credential-access result contracts,
  environment credential-presence reader, runtime credential-use boundary,
  request/result contracts, adapter port contract, and preflight guard.
- Tiingo planning metadata and fixture-safe parser/adapter boundaries for tests.
- Smoke-test suite for contracts, scope boundaries, and deterministic behavior.

## Security and Data Policy

This repository must not contain secrets, real datasets, API responses, broker
exports, database files, account files, or private validation artifacts.

Environment-specific configuration belongs outside the repository. `.env` files
are ignored, and `.env.example` is limited to non-sensitive placeholder values.
API credentials must be supplied only through local environment variables or
another approved secret-management mechanism outside version control.

See `SECURITY.md` for the full public security policy.

## Execution Governance

`PROJECT_MEMORY.md` is the private local execution authority for development
sessions and is intentionally excluded from the public release. Public status
and roadmap information lives in `docs/PUBLIC_ROADMAP.md`.

## Installation

Requirements:

- Python 3.11 or newer
- `pip`

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Running Tests

Run the full smoke suite:

```bash
python -m pytest
```

The test suite verifies current contracts, deterministic utilities, release
boundaries, and governance expectations. Passing tests do not imply source
reliability, external provider approval, live readiness, or real-data validity.

## Usage Examples

The engine utilities operate on validated in-memory records. The example below
uses synthetic values only.

```python
from datetime import date

from app.domain.data_contract import DailyMarketData
from app.domain.signal_parameters import SignalParameters
from app.engine.signals import compute_daily_signals

records = [
    DailyMarketData(date=date(2024, 1, 1), symbol="SPY", open=100, high=101, low=99, close=100, volume=1000),
    DailyMarketData(date=date(2024, 1, 2), symbol="SPY", open=100, high=102, low=100, close=101, volume=1200),
    DailyMarketData(date=date(2024, 1, 3), symbol="SPY", open=101, high=103, low=101, close=102, volume=1400),
]

parameters = SignalParameters(
    rolling_window=2,
    threshold_std=2.0,
    support_level=98.0,
    breakout_level=105.0,
    high_volume_threshold=1300.0,
    low_volume_threshold=900.0,
    low_price_movement_threshold=0.02,
    reversal_candles=1,
)

signals = compute_daily_signals(records, parameters)
```

## Limitations

- No real market dataset is included.
- No real provider API response is included.
- No source is approved for historical reliability.
- No external provider access is verified by this release.
- No persistence layer is implemented.
- No UI is implemented.
- No AI model is implemented.
- No output should be treated as a market conclusion.
- Advanced Smart Money Engine v2 research, proprietary calibration, real
  datasets, and private validation artifacts remain outside the public release.

## Roadmap

See `docs/PUBLIC_ROADMAP.md`.

Near-term public-safe priorities:

- Strengthen data quality reports and evidence records.
- Add synthetic/public-safe local CSV examples.
- Improve architecture documentation.
- Expand explainability contracts after verified data-quality foundations.

Future gated work:

- Real dataset validation workflows.
- Provider reliability evidence and cross-check processes.
- Persistence and reporting layers.
- Advanced Smart Money Engine v2 research outside this foundation release.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`.
