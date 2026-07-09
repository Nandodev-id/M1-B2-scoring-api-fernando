"""Shared fixtures for M1-B2 tests."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app

MODEL_PATH = Path(__file__).parent.parent / "models" / "pyrenex_risk_v2.joblib"


@pytest.fixture(scope="module")
def client() -> TestClient:
    """TestClient avec lifespan déclenché, donc modèle chargé."""
    if not MODEL_PATH.exists():
        pytest.skip(
            f"Modèle absent : {MODEL_PATH}. Copie d'abord ton .joblib produit "
            "en M1-B1 dans le dossier models/."
        )

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_payload() -> dict[str, Any]:
    """Payload valide aligné avec pyrenex_risk_v2.json."""
    return {
        "loan_amnt": 10000.0,
        "int_rate": 12.5,
        "installment": 334.2,
        "annual_inc": 55000.0,
        "dti": 18.5,
        "delinq_2yrs": 0.0,
        "fico_range_low": 690.0,
        "revol_util": 45.2,
        "term": "36 months",
        "grade": "B",
        "home_ownership": "RENT",
        "verification_status": "Verified",
        "purpose": "debt_consolidation",
        "emp_length": "10+ years",
    }
