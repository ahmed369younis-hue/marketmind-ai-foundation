# AGENTS.md — MarketMind AI Foundation

## Project Identity

MarketMind AI Foundation is an engine-first Smart Money Intelligence Platform foundation.

This repository is public-safe and is intended to demonstrate data-quality governance, deterministic market-structure analysis foundations, validation discipline, and AI-ready explainability planning.

This project is not:
- a trading bot
- a buy/sell signal tool
- financial advice
- a market prediction system
- a production trading system
- a live execution platform

## Execution Model

Codex must work one step at a time.

Each task must follow this sequence:

1. Understand the requested change.
2. Inspect the relevant files.
3. Make the smallest safe change.
4. Add or update tests when the change affects behavior, docs, packaging, security policy, or public release rules.
5. Run the strongest appropriate checks.
6. Review the diff.
7. Commit and push only after verified success.
8. Report exactly what changed, what tests passed, and what was pushed.

## Success Rule

A step is not successful until verification passes.

Verification may include, depending on the change:
- `python -m pytest -q -p no:cacheprovider`
- targeted pytest tests
- packaging/install verification
- README command verification
- secret scan
- git status review
- public-file safety review
- documentation consistency review

If tests fail, Codex must:
- stop
- explain the failure
- fix the failure if safe
- rerun the relevant tests
- never commit or push failing work

## Git and GitHub Progress Rule

After every successful verified step, Codex must commit and push the new or modified files to GitHub.

This is required so the public repository shows visible progress and active development.

Commit rules:
- Commit only intentional safe changes.
- Use clear professional commit messages.
- Keep commits small and meaningful.
- Do not commit generated caches.
- Do not commit private files.
- Do not commit secrets.
- Do not commit real datasets.
- Do not commit local databases.
- Do not commit logs.
- Do not commit private validation artifacts.
- Do not commit PROJECT_MEMORY.md.

Push rules:
- Push only after tests/checks pass.
- Push only to the intended repository:
  `ahmed369younis-hue/marketmind-ai-foundation`
- Do not force push unless explicitly instructed.
- Do not change repository visibility.
- Do not modify unrelated repositories.
- Do not touch `aetherx-institutional-platform`.

## Public Safety Rules

The repository must remain safe for public visibility.

Never add:
- `.env`
- `.env.*` except `.env.example`
- API keys
- access tokens
- passwords
- private keys
- broker credentials
- real market datasets
- raw API responses
- private reports
- private roadmap files
- personal/private execution history
- `PROJECT_MEMORY.md`
- `.pytest_cache/`
- `__pycache__/`
- `*.pyc`
- `*.db`
- `*.sqlite`
- `*.duckdb`
- logs
- virtual environments
- `node_modules/`
- build outputs

`.env.example` may exist only if it contains placeholders and no real values.

## Product Boundary Rules

Do not describe or implement this project as:
- an AI trading bot
- a buy/sell signal generator
- a financial advice engine
- a guaranteed profitable strategy
- a production trading system
- a market prediction platform

Allowed positioning:
- engine-first Smart Money Intelligence Platform foundation
- data quality governance
- deterministic signal foundations
- market-structure analysis foundation
- validation-first architecture
- AI-ready explainability roadmap

## Engineering Rules

Codex must prefer:
- deterministic behavior
- explicit contracts
- clear validation
- small changes
- strong tests
- readable code
- public-safe documentation
- no hidden assumptions
- no invented financial claims
- no unsupported conclusions

Codex must not:
- invent formulas without explicit approval
- introduce live trading behavior
- introduce real API fetching without explicit approval
- introduce AI/ML/LLM outputs without explicit approval
- bypass data-quality validation
- weaken security or disclaimer language
- remove tests just to make the suite pass
- hide failures

## Required Report After Each Step

After every task, Codex must return:

- STEP_STATUS: SUCCESS / NEEDS_FIXES / BLOCKED
- FILES_CHANGED
- TESTS_RUN
- TEST_RESULT
- SECRET_SCAN_RESULT if applicable
- COMMIT_HASH if committed
- PUSHED_TO_GITHUB: YES/NO
- REMOTE_URL
- NEXT_SAFE_ACTION

If no commit/push was made, Codex must clearly explain why.
