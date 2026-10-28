"""Enums for the loan approval system."""

from enum import Enum


class DecisionType(str, Enum):
    """Loan decision classifications."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class EmploymentRisk(str, Enum):
    """Employment risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    """Financial risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApplicationStatus(str, Enum):
    """Loan application status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CreditRating(str, Enum):
    """Credit score ratings."""

    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    VERY_GOOD = "very_good"
    EXCELLENT = "excellent"
