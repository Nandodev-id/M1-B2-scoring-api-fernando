"""Pydantic schemas for the Pyrenex Risk API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoanApplication(BaseModel):
    """Input schema for /predict aligned with pyrenex_risk_v2 metadata."""

    model_config = ConfigDict(extra="forbid", strict=True)

    loan_amnt: float = Field(..., ge=500, le=40_000, description="Loan amount")
    int_rate: float = Field(..., ge=0, le=50, description="Interest rate")
    installment: float = Field(..., ge=0, description="Monthly installment")
    annual_inc: float = Field(..., ge=0, le=10_000_000, description="Annual income")
    dti: float = Field(..., ge=0, le=100, description="Debt-to-income ratio")
    delinq_2yrs: float = Field(..., ge=0, description="Delinquencies in last 2 years")
    fico_range_low: float = Field(..., ge=300, le=850, description="Lower FICO score range")
    revol_util: float = Field(..., ge=0, le=150, description="Revolving credit utilization")

    term: str = Field(..., description="Loan term, e.g. '36 months' or '60 months'")
    grade: str = Field(..., description="Loan grade")
    home_ownership: str = Field(..., description="Home ownership status")
    verification_status: str = Field(..., description="Income verification status")
    purpose: str = Field(..., description="Loan purpose")
    emp_length: str = Field(..., description="Employment length")


class Prediction(BaseModel):
    """Output schema for /predict."""

    prediction: int = Field(..., description="0 = Fully Paid, 1 = Charged Off")
    probability: float = Field(..., ge=0.0, le=1.0)
    model_version: str
    request_id: str


class HealthResponse(BaseModel):
    """Output schema for /health."""

    status: str
