from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_workflow_exists_with_required_public_verification_steps() -> None:
    content = CI_WORKFLOW_PATH.read_text(encoding="utf-8")

    required_phrases = [
        "name: CI",
        "push:",
        "pull_request:",
        "runs-on: ubuntu-latest",
        "actions/checkout@v4",
        "actions/setup-python@v5",
        'python-version: "3.11"',
        'python -m pip install -e ".[dev]"',
        "python -m pytest -q -p no:cacheprovider",
    ]

    assert CI_WORKFLOW_PATH.is_file()
    for phrase in required_phrases:
        assert phrase in content
