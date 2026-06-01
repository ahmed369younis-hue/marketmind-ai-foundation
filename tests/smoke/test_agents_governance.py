from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"


def test_agents_governance_file_exists_with_public_safe_rules() -> None:
    content = AGENTS_PATH.read_text(encoding="utf-8")

    required_phrases = [
        "MarketMind AI Foundation",
        "engine-first Smart Money Intelligence Platform foundation",
        "public-safe",
        "data-quality governance",
        "AI-ready explainability planning",
        "not:",
        "a trading bot",
        "a buy/sell signal tool",
        "financial advice",
        "a market prediction system",
        "a production trading system",
        "live execution platform",
        "PROJECT_MEMORY.md",
        "Push only to the intended repository",
        "ahmed369younis-hue/marketmind-ai-foundation",
        "Do not touch `aetherx-institutional-platform`",
        "STEP_STATUS: SUCCESS / NEEDS_FIXES / BLOCKED",
    ]

    assert AGENTS_PATH.is_file()
    for phrase in required_phrases:
        assert phrase in content
