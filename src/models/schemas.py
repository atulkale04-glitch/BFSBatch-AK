"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.enums import DecisionType, EmploymentRisk


class LoanApplicationRequest(BaseModel):
    """Loan application submission request."""

    applicant_id: str = Field(..., min_length=1, description="Unique applicant identifier")
    age: int = Field(..., ge=18, le=100, description="Applicant age")
    income: float = Field(..., gt=0, description="Annual income")
    employment_type: str = Field(..., min_length=1, description="Type of employment")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_tenure_months: int = Field(..., gt=0, le=360, description="Loan tenure in months")
    existing_liabilities: float = Field(..., ge=0, description="Total existing liabilities")
    location: str = Field(..., min_length=1, description="Applicant location")
    application_timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Application submission time"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "applicant_id": "APP-001",
                "age": 35,
                "income": 75000.0,
                "employment_type": "Full-time",
                "credit_score": 720,
                "loan_amount": 250000.0,
                "loan_tenure_months": 360,
                "existing_liabilities": 50000.0,
                "location": "New York",
            }
        }


class ApplicationSubmissionResponse(BaseModel):
    """Response to application submission."""

    application_id: str = Field(..., description="Unique application identifier")
    status: str = Field(..., description="Current application status")
    created_at: datetime = Field(..., description="Application creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "LOAN-20240101-00001",
                "status": "processing",
                "created_at": "2024-01-01T10:30:00Z",
            }
        }


class ApplicantProfileOutput(BaseModel):
    """Output from Applicant Profile Agent."""

    income_stability_score: float = Field(..., ge=0, le=100, description="Income stability score")
    employment_risk: EmploymentRisk = Field(..., description="Employment risk level")
    credit_history_summary: str = Field(..., description="Summary of credit history")
    completeness_flags: List[str] = Field(default_factory=list, description="Missing or incomplete fields")


class FinancialRiskOutput(BaseModel):
    """Output from Financial Risk Analysis Agent."""

    dti_ratio: float = Field(..., ge=0, description="Debt-to-income ratio")
    dti_risk_level: str = Field(..., description="DTI risk assessment")
    credit_score_risk: str = Field(..., description="Credit score risk level")
    loan_amount_risk: str = Field(..., description="Loan amount risk assessment")
    anomaly_flags: List[str] = Field(default_factory=list, description="Detected anomalies")
    risk_reasoning: str = Field(..., description="Detailed risk analysis reasoning")


class LoanDecisionOutput(BaseModel):
    """Output from Loan Decision Agent."""

    decision: DecisionType = Field(..., description="Loan approval decision")
    risk_score: float = Field(..., ge=0, le=100, description="Composite risk score")
    confidence_level: float = Field(..., ge=0, le=100, description="Decision confidence level")
    key_factors: List[str] = Field(..., description="Key factors influencing decision")
    explanation: str = Field(..., description="Detailed explanation of decision")


class LoanDecisionResponse(BaseModel):
    """Final loan decision response."""

    application_id: str = Field(..., description="Loan application ID")
    decision: DecisionType = Field(..., description="Loan approval decision")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0-100)")
    confidence_level: float = Field(..., ge=0, le=100, description="Confidence level (0-100%)")
    key_factors: List[str] = Field(..., description="Key decision factors")
    explanation: str = Field(..., description="Detailed decision explanation")
    case_id: str = Field(..., description="Unique case identifier")
    timestamp: datetime = Field(..., description="Decision timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "LOAN-20240101-00001",
                "decision": "APPROVED",
                "risk_score": 35,
                "confidence_level": 92,
                "key_factors": [
                    "Strong credit history",
                    "Low DTI ratio",
                    "Stable employment",
                ],
                "explanation": "Application approved based on strong financial profile...",
                "case_id": "CASE-20240101-00001",
                "timestamp": "2024-01-01T10:35:00Z",
            }
        }


class ApplicationStatusResponse(BaseModel):
    """Current application status."""

    application_id: str = Field(..., description="Loan application ID")
    status: str = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    decision: Optional[str] = Field(None, description="Decision if completed")
