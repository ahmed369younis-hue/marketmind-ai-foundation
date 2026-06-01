from pathlib import Path
from types import SimpleNamespace

import pytest

from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.local_csv_batch_run import (
    LocalCsvBatchRunResult,
    LocalCsvBatchRunStatus,
)
from app.domain.local_csv_quality_validation import LocalCsvQualityValidationResult


def _validation_result(
    *,
    ingestion_status: DataIngestionStatus,
    quality_gate_passed: bool,
) -> LocalCsvQualityValidationResult:
    validation_result = object.__new__(LocalCsvQualityValidationResult)
    object.__setattr__(
        validation_result,
        "batch",
        SimpleNamespace(result=SimpleNamespace(status=ingestion_status)),
    )
    object.__setattr__(validation_result, "quality_results", [])
    object.__setattr__(validation_result, "quality_gate_passed", quality_gate_passed)
    return validation_result


def _run_result(**overrides: object) -> LocalCsvBatchRunResult:
    values = {
        "validation_result": _validation_result(
            ingestion_status=DataIngestionStatus.SUCCESS,
            quality_gate_passed=True,
        ),
        "status": LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING,
        "run_label": "Local CSV batch run contract test.",
        "notes": "Contract-only test record.",
    }
    values.update(overrides)
    return LocalCsvBatchRunResult(**values)


def test_ready_for_engine_planning_passes_when_success_and_gate_passed() -> None:
    result = _run_result(
        validation_result=_validation_result(
            ingestion_status=DataIngestionStatus.SUCCESS,
            quality_gate_passed=True,
        ),
        status=LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING,
    )

    assert isinstance(result, LocalCsvBatchRunResult)


def test_blocked_by_quality_gate_passes_when_success_and_gate_failed() -> None:
    result = _run_result(
        validation_result=_validation_result(
            ingestion_status=DataIngestionStatus.SUCCESS,
            quality_gate_passed=False,
        ),
        status=LocalCsvBatchRunStatus.BLOCKED_BY_QUALITY_GATE,
    )

    assert isinstance(result, LocalCsvBatchRunResult)


def test_failed_ingestion_passes_when_ingestion_failed() -> None:
    result = _run_result(
        validation_result=_validation_result(
            ingestion_status=DataIngestionStatus.FAILED,
            quality_gate_passed=False,
        ),
        status=LocalCsvBatchRunStatus.FAILED_INGESTION,
    )

    assert isinstance(result, LocalCsvBatchRunResult)


def test_non_local_csv_quality_validation_result_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(validation_result="not a validation result")


def test_invalid_status_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(status="READY_FOR_ENGINE_PLANNING")


def test_empty_run_label_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(run_label=" ")


def test_empty_notes_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(notes=" ")


def test_failed_ingestion_with_ready_for_engine_planning_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(
            validation_result=_validation_result(
                ingestion_status=DataIngestionStatus.FAILED,
                quality_gate_passed=False,
            ),
            status=LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING,
        )


def test_failed_ingestion_with_blocked_by_quality_gate_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(
            validation_result=_validation_result(
                ingestion_status=DataIngestionStatus.FAILED,
                quality_gate_passed=False,
            ),
            status=LocalCsvBatchRunStatus.BLOCKED_BY_QUALITY_GATE,
        )


def test_success_failed_quality_gate_with_ready_for_engine_planning_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(
            validation_result=_validation_result(
                ingestion_status=DataIngestionStatus.SUCCESS,
                quality_gate_passed=False,
            ),
            status=LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING,
        )


def test_success_passed_quality_gate_with_blocked_by_quality_gate_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _run_result(
            validation_result=_validation_result(
                ingestion_status=DataIngestionStatus.SUCCESS,
                quality_gate_passed=True,
            ),
            status=LocalCsvBatchRunStatus.BLOCKED_BY_QUALITY_GATE,
        )


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        LocalCsvBatchRunResult()


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/domain/local_csv_batch_run.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_engine_imports_are_introduced() -> None:
    source = Path("app/domain/local_csv_batch_run.py").read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source
