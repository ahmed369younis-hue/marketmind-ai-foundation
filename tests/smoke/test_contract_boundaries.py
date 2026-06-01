from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONTRACT_FILES = [
    "app/domain/data_contract.py",
    "app/domain/feature_contract.py",
    "app/domain/signal_contract.py",
    "app/domain/score_contract.py",
    "app/domain/market_phase_contract.py",
    "app/domain/confidence_contract.py",
]

FORBIDDEN_INDICATORS = [
    "rolling_std",
    "moving_avg",
    "slope(",
    "raw_score",
    "smart_money_score =",
    "confidence =",
    "signal_agreement",
    "consistency",
    "price_change",
    "return_N",
    "breakout",
    "support_level",
    "threshold_std",
    "validation_engine",
    "pandas",
    "numpy",
]


def test_domain_contracts_do_not_contain_calculation_logic() -> None:
    for contract_file in CONTRACT_FILES:
        content = (PROJECT_ROOT / contract_file).read_text(encoding="utf-8")

        for forbidden_indicator in FORBIDDEN_INDICATORS:
            assert forbidden_indicator not in content, (
                f"{contract_file} contains forbidden calculation/business logic "
                f"indicator: {forbidden_indicator}"
            )
