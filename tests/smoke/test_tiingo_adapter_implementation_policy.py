from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_record_tiingo_adapter_boundary_policy() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "Tiingo planning/test boundaries",
        "planning and test boundaries only",
        "fixture payloads",
        "fake transports",
        "injected callables",
        "No real Tiingo response payload",
        "No external provider access is approved by this public release",
        "No source is approved for historical reliability",
        "No provider API response data is included",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
