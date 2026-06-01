from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_record_runtime_credential_policy() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    public_docs = f"{roadmap}\n{security}"

    required_phrases = [
        "Credential handling must remain secret-safe",
        "must not read `.env`",
        "print raw credentials",
        "store raw credentials",
        "write raw credentials to fixtures",
        "place raw credentials in public documentation",
        "API keys must be supplied only through local environment variables",
        "Keys must not be printed, logged, stored in fixtures",
        ".env files must never be committed",
    ]

    for phrase in required_phrases:
        assert phrase in public_docs
