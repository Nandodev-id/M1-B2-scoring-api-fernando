"""Contract test du modèle servi par l'API."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import pytest

MODEL_PATH = Path(__file__).parent.parent / "models" / "pyrenex_risk_v2.joblib"
META_PATH = Path(__file__).parent.parent / "models" / "pyrenex_risk_v2.json"


@pytest.fixture(scope="module")
def loaded_model():
    """Charge exactement le .joblib que l'API sert via lifespan."""
    if not MODEL_PATH.exists():
        pytest.skip(
            f"Modèle absent : {MODEL_PATH}. Copie d'abord ton .joblib produit "
            "en M1-B1 dans le dossier models/."
        )
    return joblib.load(MODEL_PATH)


@pytest.fixture(scope="module")
def model_metadata() -> dict[str, Any]:
    """Charge les métadonnées du modèle packagé."""
    if not META_PATH.exists():
        pytest.skip(f"Métadonnées absentes : {META_PATH}")

    return json.loads(META_PATH.read_text(encoding="utf-8"))


def test_model_contract(
    loaded_model,
    model_metadata: dict[str, Any],
    valid_payload: dict[str, Any],
) -> None:
    """Le modèle persisté respecte le contrat attendu par l'API."""
    numeric_columns = model_metadata["feature_columns"]["numeric"]
    categorical_columns = model_metadata["feature_columns"]["categorical"]
    ordered_columns = [*numeric_columns, *categorical_columns]

    x_input = pd.DataFrame([valid_payload], columns=ordered_columns)

    prediction = loaded_model.predict(x_input)
    proba = loaded_model.predict_proba(x_input)

    assert prediction.shape == (1,), f"shape predict={prediction.shape}, attendu (1,)"
    assert proba.shape == (1, 2), f"shape predict_proba={proba.shape}, attendu (1, 2)"
    assert set(loaded_model.classes_) == {0, 1}
    assert int(prediction[0]) in (0, 1)
    assert 0.0 <= float(proba.min()) <= 1.0
    assert 0.0 <= float(proba.max()) <= 1.0
