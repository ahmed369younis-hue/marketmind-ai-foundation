from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_record_local_csv_data_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    public_docs = f"{roadmap}\n{readme}"

    required_text = [
        "Local CSV support is currently a validation foundation only",
        "data/raw",
        "data/processed",
        "artifacts",
        "real datasets",
        "private validation outputs are excluded",
        "No real market dataset is included",
        "No real data conclusions are produced",
        "No output should be treated as a market conclusion",
    ]

    for text in required_text:
        assert text in public_docs
