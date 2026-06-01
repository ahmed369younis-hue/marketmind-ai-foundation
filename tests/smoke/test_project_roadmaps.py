from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ROADMAP_PATH = REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md"


def test_public_roadmap_records_current_phase_and_future_boundaries() -> None:
    roadmap = PUBLIC_ROADMAP_PATH.read_text(encoding="utf-8")

    required_text = [
        "Current Phase",
        "Phase 2: Data & Validation",
        "Implemented Public-Safe Components",
        "Data Quality Gate",
        "local CSV ingestion",
        "No AI model is currently implemented",
        "No real data conclusions are produced",
        "AI-ready explainability roadmap",
        "Future Roadmap",
        "Advanced Smart Money Engine v2 research",
    ]

    for text in required_text:
        assert text in roadmap
