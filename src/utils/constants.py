"""System constants and configuration values."""

import uuid
from datetime import datetime

# System-wide constants
SYSTEM_NAME = "Loan Approval System"
SYSTEM_VERSION = "1.0.0"

# ID Generation
def generate_application_id() -> str:
    """Generate unique application ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_id = str(uuid.uuid4())[:8].upper()
    return f"LOAN-{timestamp}-{random_id}"


def generate_case_id() -> str:
    """Generate unique case ID for decision record."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_id = str(uuid.uuid4())[:8].upper()
    return f"CASE-{timestamp}-{random_id}"


def generate_evaluation_id() -> str:
    """Generate unique evaluation ID."""
    return f"EVAL-{str(uuid.uuid4())[:12].upper()}"


# Agent names
AGENT_APPLICANT_PROFILE = "applicant_profile_agent"
AGENT_FINANCIAL_RISK = "financial_risk_agent"
AGENT_LOAN_DECISION = "loan_decision_agent"
AGENT_COMPLIANCE = "compliance_orchestrator_agent"

# Decision types
DECISION_APPROVED = "APPROVED"
DECISION_REJECTED = "REJECTED"
DECISION_MANUAL_REVIEW = "MANUAL_REVIEW"

# Application status
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Risk levels
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"

# Employment types
EMPLOYMENT_TYPES = [
    "Full-time",
    "Part-time",
    "Self-employed",
    "Retired",
    "Student",
    "Unemployed",
]

# Default timeouts (in seconds)
DEFAULT_AGENT_TIMEOUT = 30
DEFAULT_API_TIMEOUT = 60
DEFAULT_MCP_TIMEOUT = 30

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
