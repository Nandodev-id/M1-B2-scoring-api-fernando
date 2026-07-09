"""Pyrenex Risk API — entry point.

TODO — Complete the routes /info and /predict.
"""
from __future__ import annotations

import json
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, status
from loguru import logger

from app.middleware import LoggingMiddleware
from app.schemas import HealthResponse, LoanApplication, Prediction

# --- Loguru configuration ---------------------------------------------------

LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stderr, level="INFO", colorize=True)
logger.add(
    LOGS_DIR / "api.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    serialize=True,
    enqueue=True,
    level="INFO",
)


# --- Lifespan ---------------------------------------------------------------

MODELS_DIR = Path(__file__).parent.parent / "models"
MODEL_PATH = MODELS_DIR / "pyrenex_risk_v2.joblib"
META_PATH = MODELS_DIR / "pyrenex_risk_v2.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model + metadata at startup, release at shutdown."""
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found at {MODEL_PATH}")
    if not META_PATH.exists():
        raise RuntimeError(f"Metadata file not found at {META_PATH}")

    app.state.model = joblib.load(MODEL_PATH)
    app.state.metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    logger.info(
        "Model loaded: {name} {version}",
        # .get() with fallback: the M1-B1 metadata contract does not force
        # "model_name" — the API must not crash on a contract-compliant file
        name=app.state.metadata.get("model_name", MODEL_PATH.stem),
        version=app.state.metadata["model_version"],
    )
    yield
    app.state.model = None
    logger.info("Model released")


app = FastAPI(
    title="Pyrenex Risk API",
    version="0.1.0",
    description="API serving the Pyrenex Crédit credit-risk scoring model.",
    lifespan=lifespan,
)
app.add_middleware(LoggingMiddleware)


# --- Routes -----------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness check."""
    if not hasattr(app.state, "model") or app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return HealthResponse(status="ok")


@app.get("/info")
async def info() -> dict:
    """Return loaded model metadata."""
    if not hasattr(app.state, "metadata") or app.state.metadata is None:
        raise HTTPException(status_code=503, detail="Metadata not loaded")

    metadata = app.state.metadata

    required_keys = [
        "model_version",
        "created_at",
        "sklearn_version",
        "dataset_sha256",
        "metrics_holdout",
    ]

    missing_keys = [key for key in required_keys if metadata.get(key) is None]
    if missing_keys:
        raise HTTPException(
            status_code=500,
            detail=f"Missing metadata keys: {missing_keys}",
        )

    return {
        "api_version": app.version,
        "model_name": metadata.get("model_name", MODEL_PATH.stem),
        "model_version": metadata["model_version"],
        "created_at": metadata["created_at"],
        "sklearn_version": metadata["sklearn_version"],
        "dataset_sha256": metadata["dataset_sha256"],
        "metrics_holdout": metadata["metrics_holdout"],
    }


@app.post("/predict", response_model=Prediction, status_code=status.HTTP_200_OK)
async def predict(application: LoanApplication, request: Request) -> Prediction:
    """Predict default risk for one loan application."""
    if not hasattr(app.state, "model") or app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not hasattr(app.state, "metadata") or app.state.metadata is None:
        raise HTTPException(status_code=503, detail="Metadata not loaded")

    model = app.state.model
    metadata = app.state.metadata

    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    try:
        feature_columns = metadata["feature_columns"]
        numeric_columns = feature_columns["numeric"]
        categorical_columns = feature_columns["categorical"]
        ordered_columns = [*numeric_columns, *categorical_columns]

        application_data = application.model_dump()
        input_df = pd.DataFrame([application_data], columns=ordered_columns)

        prediction = int(model.predict(input_df)[0])
        probabilities = model.predict_proba(input_df)[0]

        classes = list(model.classes_)
        prediction_index = classes.index(prediction)
        probability = float(probabilities[prediction_index])

        return Prediction(
            prediction=prediction,
            probability=probability,
            model_version=metadata["model_version"],
            request_id=request_id,
        )

    except Exception as exc:
        logger.exception(
            "Prediction failed",
            request_id=request_id,
            error=str(exc),
        )
        raise HTTPException(
            status_code=500,
            detail="Prediction failed",
        ) from exc
