from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_record_first_provider_boundary_policy() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "Tiingo references in the public foundation are planning and test boundaries",
        "No real Tiingo response payload",
        "API key",
        "provider validation artifact is included",
        "do not approve a provider",
        "approve source reliability",
        "approve live use",
        "produce market conclusions",
        "No external provider access is approved by this public release",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
