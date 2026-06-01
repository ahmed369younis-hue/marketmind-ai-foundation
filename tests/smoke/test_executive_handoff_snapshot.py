from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_contain_release_identity_and_boundaries() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    public_docs = f"{readme}\n{roadmap}"

    required_text = [
        "Engine-first Smart Money Intelligence Platform",
        "data quality governance",
        "deterministic signal foundations",
        "AI-ready explainability roadmap",
        "No trading advice is provided",
        "No AI model is currently implemented",
        "No real data conclusions are produced",
        "No live broker or exchange integration is included",
        "No UI is implemented",
        "Private project memory is intentionally excluded from the public release",
        "This repository is intended to show architecture, governance",
    ]

    for text in required_text:
        assert text in public_docs
