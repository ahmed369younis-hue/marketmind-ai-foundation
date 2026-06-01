from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_record_managed_api_data_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    public_docs = f"{roadmap}\n{security}"

    required_text = [
        "Managed API code is boundary-oriented",
        "credential-access result contracts",
        "runtime credential-use boundary",
        "fetch request/result contracts",
        "preflight guards",
        "do not approve a provider",
        "verify provider access",
        "verify credential correctness",
        "ingest API data",
        "persist data",
        "produce market conclusions",
        "API keys must be supplied only through local environment variables",
    ]

    for text in required_text:
        assert text in public_docs
