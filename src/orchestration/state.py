"""Workflow state management using TypedDict for type safety."""

from typing import Any, Dict, List, Optional, TypedDict


class WorkflowState(TypedDict, total=False):
    """Complete workflow state for loan application processing."""

    # Application identification
    application_id: str
    applicant_id: str
    case_id: str

    # Application data
    application_data: Dict[str, Any]
    age: int
    income: float
    employment_type: str
    credit_score: int
    loan_amount: float
    loan_tenure_months: int
    existing_liabilities: float
    location: str
    applicant_email: str

    # Status tracking
    status: str  # "pending" | "processing" | "completed" | "failed"
    error_message: Optional[str]
    current_step: str

    # Agent outputs
    applicant_profile_output: Optional[Dict[str, Any]]
    financial_risk_output: Optional[Dict[str, Any]]
    loan_decision_output: Optional[Dict[str, Any]]
    compliance_output: Optional[Dict[str, Any]]

    # Intermediate results
    evaluations: Dict[str, Dict[str, Any]]
    composite_risk_score: Optional[float]
    conflicting_recommendations: Optional[List[str]]

    # Final decision
    final_decision: Optional[str]  # "APPROVED" | "REJECTED" | "MANUAL_REVIEW"
    risk_score: Optional[float]
    confidence_level: Optional[float]
    key_factors: List[str]
    reasoning: Optional[str]

    # Audit trail
    audit_entries: List[Dict[str, Any]]
    notifications_sent: List[str]

    # Metadata
    created_at: str
    updated_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    iterations: int


def create_initial_state(application_id: str, applicant_id: str, application_data: Dict[str, Any]) -> WorkflowState:
    """Create initial workflow state from application data."""
    from datetime import datetime

    return {
        "application_id": application_id,
        "applicant_id": applicant_id,
        "application_data": application_data,
        # Extract fields from application data
        "age": application_data.get("age", 0),
        "income": application_data.get("income", 0),
        "employment_type": application_data.get("employment_type", ""),
        "credit_score": application_data.get("credit_score", 0),
        "loan_amount": application_data.get("loan_amount", 0),
        "loan_tenure_months": application_data.get("loan_tenure_months", 0),
        "existing_liabilities": application_data.get("existing_liabilities", 0),
        "location": application_data.get("location", ""),
        "applicant_email": application_data.get("applicant_email", ""),
        # Status
        "status": "pending",
        "error_message": None,
        "current_step": "initialization",
        # Agent outputs (None initially)
        "applicant_profile_output": None,
        "financial_risk_output": None,
        "loan_decision_output": None,
        "compliance_output": None,
        # Intermediate
        "evaluations": {},
        "composite_risk_score": None,
        "conflicting_recommendations": None,
        # Decision
        "final_decision": None,
        "risk_score": None,
        "confidence_level": None,
        "key_factors": [],
        "reasoning": None,
        # Audit
        "audit_entries": [],
        "notifications_sent": [],
        # Metadata
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "iterations": 0,
    }


def update_state_status(state: WorkflowState, status: str, step: str = "", error: Optional[str] = None) -> None:
    """Update workflow state status."""
    from datetime import datetime

    state["status"] = status
    if step:
        state["current_step"] = step
    state["updated_at"] = datetime.utcnow().isoformat()
    if error:
        state["error_message"] = error
    if status == "processing" and not state.get("started_at"):
        state["started_at"] = datetime.utcnow().isoformat()
    if status == "completed":
        state["completed_at"] = datetime.utcnow().isoformat()


def add_audit_entry(state: WorkflowState, action: str, details: Dict[str, Any]) -> None:
    """Add an entry to the audit trail."""
    from datetime import datetime

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details,
    }
    state["audit_entries"].append(entry)


def merge_evaluation(state: WorkflowState, agent_name: str, evaluation: Dict[str, Any]) -> None:
    """Merge agent evaluation into state."""
    if "evaluations" not in state:
        state["evaluations"] = {}
    state["evaluations"][agent_name] = evaluation
    add_audit_entry(state, f"EVALUATION_{agent_name.upper()}", {"evaluation": evaluation})
