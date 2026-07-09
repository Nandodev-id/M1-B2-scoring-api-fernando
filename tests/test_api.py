"""M1-B2 — API tests."""
from __future__ import annotations
import pytest
from typing import Any

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    """/health returns 200 and the expected status."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_info_returns_required_metadata(client: TestClient) -> None:
    """/info exposes API version and mandatory model metadata."""
    response = client.get("/info")

    assert response.status_code == 200

    data = response.json()
    required_keys = {
        "api_version",
        "model_version",
        "created_at",
        "sklearn_version",
        "dataset_sha256",
        "metrics_holdout",
    }

    assert required_keys.issubset(data.keys())
    assert all(data[key] is not None for key in required_keys)
    assert data["model_version"] == "v2.0.0"


def test_predict_valid_payload(
    client: TestClient,
    valid_payload: dict[str, Any],
) -> None:
    """/predict returns 200 with a well-formed response on valid input."""
    response = client.post("/predict", json=valid_payload)

    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] in (0, 1)
    assert 0.0 <= data["probability"] <= 1.0
    assert data["model_version"] == "v2.0.0"
    assert data["request_id"]
    assert "X-Request-ID" in response.headers


def test_predict_missing_field_returns_422(
    client: TestClient,
    valid_payload: dict[str, Any],
) -> None:
    """/predict returns 422 on missing required field."""
    invalid = {
        key: value
        for key, value in valid_payload.items()
        if key != "loan_amnt"
    }

    response = client.post("/predict", json=invalid)

    assert response.status_code == 422
    assert "loan_amnt" in response.text


def test_predict_unknown_field_returns_422(
    client: TestClient,
    valid_payload: dict[str, Any],
) -> None:
    """/predict returns 422 when an unknown field is sent."""
    invalid = valid_payload | {"unknown_field": "not allowed"}

    response = client.post("/predict", json=invalid)

    assert response.status_code == 422
    assert "unknown_field" in response.text


def test_predict_is_deterministic(
    client: TestClient,
    valid_payload: dict[str, Any],
) -> None:
    """Same input should produce the same prediction and probability."""
    first_response = client.post("/predict", json=valid_payload)
    second_response = client.post("/predict", json=valid_payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["prediction"] == second_data["prediction"]
    assert first_data["probability"] == pytest.approx(
        second_data["probability"],
        rel=1e-12,
        abs=1e-12,
    )