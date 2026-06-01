from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_record_provider_response_parsing_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "fixture payloads",
        "fake transports",
        "injected callables",
        "No real Tiingo response payload",
        "No provider API response data is included",
        "No real provider API response is included",
        "No real data conclusions are produced",
        "produce market conclusions",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
