# Multi-Asset Data Acquisition Strategy

## Purpose

This document defines future real-data acquisition governance for a multi-asset
MarketMind AI platform. It is strategy and governance only, not implementation.

It does not implement data fetching, ingestion, persistence, engine execution,
provider approval, source reliability approval, market analysis, trading output,
or financial conclusions.

## Asset Coverage

Future multi-asset planning covers:

- Gold
- Oil
- Bitcoin
- EUR/USD

US Equities / ETFs remain the first execution market using Daily EOD local CSV
under the current approved roadmap. Multi-asset expansion must not bypass local
CSV validation maturity, data quality governance, source reliability controls,
or explicit future implementation approval.

## Data-Source Tiers

- Tier 0: Synthetic/public-safe fixtures for tests only.
- Tier 1: Local CSV validation path.
- Tier 2: ETF proxy path for early commodity exposure planning, such as
  gold/oil ETF-style exposure, without claiming provider approval.
- Tier 3: Direct institutional data providers for future spot, futures, FX, or
  crypto data, requiring separate documentation evidence and access
  verification.
- Tier 4: Cross-check providers for independent validation and discrepancy
  detection.
- Tier 5: Future internal curated datasets after source governance, quality
  gates, and storage rules exist.

## Cross-Source Validation Governance

A cross-source validation policy contract exists for future planning. A cross-source validation policy evaluation gate exists for metadata-only planning readiness only.
These boundaries check planned source roles and asset-specific
references before any future data-source planning step.

They do not:

- validate real data
- select or approve any provider
- approve source reliability
- verify historical reliability
- assign VERIFIED_HISTORICAL
- approve production use
- run ingestion
- execute the Data Quality Gate
- run engine logic
- produce market analysis, trading output, buy/sell output, or financial
  conclusions

## Asset-Specific Requirements

### US Equities / ETFs

- First execution market using Daily EOD local CSV.
- Requires exchange/ETF session governance for the first execution market.
- Requires adjusted/unadjusted price policy and corporate action policy.
- Requires independent cross-source planning before reliability claims.
- Requires timestamp, price, and volume consistency planning.
- Does not require futures roll, FX quote validation, or crypto exchange cross-check policy.

### Gold

- Early path may use ETF-style proxy planning before direct spot or futures
  complexity.
- Direct gold data later requires source policy, session policy, pricing
  convention, timezone policy, and validation rules.
- Gold futures later require contract expiry and roll logic.

### Oil

- Early path may use ETF or energy proxy planning before futures complexity.
- Oil futures later require contract expiry, roll logic, contract selection
  policy, and calendar/session handling.

### Bitcoin

- Requires 24/7 calendar handling.
- Requires exchange-source policy.
- Requires volume fragmentation handling.
- Requires cross-exchange validation before reliability claims.

### EUR/USD

- Requires FX session handling.
- Must not treat FX volume like centralized equity volume.
- Requires non-centralized-volume or liquidity-proxy policy before engine
  interpretation.
- Requires source-specific quote and timestamp validation.

## Provider Governance

No provider is approved by this document. No vendor is selected by this document.

Candidate providers may be mentioned in future planning only as unapproved,
documentation-evidence-gated candidates. Any provider must later pass:

- documentation evidence
- legal credential/access confirmation
- source metadata evaluation
- fetch preflight
- response parsing
- data quality evaluation
- Data Quality Gate
- cross-check policy if required

No metadata or credential presence may imply source reliability approval. No Data Quality Gate pass alone may imply historical verification or production approval.

## Data Quality Requirements

Future real-data acquisition must define and verify, as applicable:

- schema validation
- date/time validation
- missing data checks
- duplicate record checks
- OHLC relationship checks where applicable
- adjusted/unadjusted price policy where applicable
- timezone/session/calendar validation
- source consistency and cross-check rules
- gap and coverage reporting
- evidence report generation

## Strict Prohibitions

This governance step creates no permission for:

- API call implementation
- real data download
- provider response fixtures from real APIs
- persistence
- database
- engine execution
- signals, scores, phase, or confidence output
- buy/sell/trading output
- market analysis
- financial conclusions
- production approval
- source reliability approval
- VERIFIED_HISTORICAL classification

CSV parsing success must not be treated as market-data validity. Data Quality
Gate pass must not be treated as historical verification, production approval,
source reliability approval, or permission for financial conclusions.

## Future Implementation Gates

- Local CSV path must remain first.
- Asset-specific requirements must exist before multi-asset implementation.
- Real local CSV batch execution must be separately scoped.
- Managed API fetch must be separately scoped.
- Provider access verification must be separately scoped.
- Real-data ingestion must be separately scoped.
- Engine execution must require explicit future approval after quality validation.
